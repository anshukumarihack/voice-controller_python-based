"""
VoiceAssistant: Core class integrating Vosk ASR with command dispatcher
Improved version with better accuracy, overflow fix, and lower confidence threshold
"""

import csv
import os
import json
import queue
import threading
import logging
import numpy as np
from datetime import datetime
from pathlib import Path

import sounddevice as sd
from vosk import Model, KaldiRecognizer

from commands.dispatcher import CommandDispatcher
from utils.noise_filter import NoiseFilter
from utils.feedback import AudioFeedback

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("assistant.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SAMPLE_RATE          = 16000
BLOCK_SIZE           = 4000        # smaller = less overflow
MODEL_DIR            = Path(__file__).resolve().parent / "models"
MODEL_FALLBACKS      = [
    "vosk-model-small-en-in",
    "vosk-model-small-en-us",
]
CONFIDENCE_THRESHOLD = 0.40        # lowered for better recognition
WAKE_WORDS           = {
    "hey google",
    "ok",
    "assistant",
    "hey",
    "start",
    "p",
    "hello",
    "hi assistant",
    "okay assistant",
}


class VoiceAssistant:
    """
    Offline voice assistant pipeline:
      Mic -> NoiseFilter -> Vosk ASR -> CommandDispatcher -> PyAutoGUI
    """

    def __init__(self):
        self._running        = False
        self._listening      = False
        self._audio_queue    = queue.Queue(maxsize=50)
        self._thread         = None

        self.noise_filter    = NoiseFilter()
        self.feedback        = AudioFeedback()
        self.dispatcher      = CommandDispatcher()

        self.model           = self._load_model()
        self.recognizer      = KaldiRecognizer(self.model, SAMPLE_RATE)
        self.recognizer.SetWords(True)

        self.total_commands   = 0
        self.matched_commands = 0

        self._accuracy_log_path = (
            Path(__file__).resolve().parent.parent / "logs" / "accuracy_log.csv"
        )
        self._init_accuracy_log()

        logger.info("VoiceAssistant initialised - wake words: %s", WAKE_WORDS)

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info("Assistant started - say a wake word to begin.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Assistant stopped.")

    def toggle_listening(self):
        self._listening = not self._listening
        state = "active" if self._listening else "paused"
        logger.info("Listening %s", state)
        return self._listening

    @property
    def accuracy(self):
        if self.total_commands == 0:
            return 0.0
        return self.matched_commands / self.total_commands

    # ------------------------------------------------------------------ #
    #  Internal pipeline                                                   #
    # ------------------------------------------------------------------ #

    def _load_model(self):
        if not MODEL_DIR.exists():
            logger.error(
                "Models folder not found at %s. Create it and add a Vosk model.",
                MODEL_DIR,
            )
            raise FileNotFoundError(
                "Models directory missing. Create a models/ folder and add a Vosk model."
            )

        for candidate in MODEL_FALLBACKS:
            model_path = MODEL_DIR / candidate
            if model_path.exists():
                logger.info("Loading Vosk model from %s ...", model_path)
                return Model(str(model_path))

        for candidate_path in sorted(MODEL_DIR.iterdir()):
            if candidate_path.is_dir() and candidate_path.name.startswith("vosk-model"):
                logger.info("Loading Vosk model from %s ...", candidate_path)
                return Model(str(candidate_path))

        available = [p.name for p in MODEL_DIR.iterdir() if p.is_dir()]
        logger.error(
            "No Vosk model found in %s. Expected one of: %s. Available folders: %s",
            MODEL_DIR,
            ", ".join(MODEL_FALLBACKS),
            ", ".join(available) if available else "(none)"
        )
        raise FileNotFoundError(
            "Vosk model missing. Download and extract a compatible model into the models/ folder. "
            "For example: models/vosk-model-small-en-us"
        )

    def _init_accuracy_log(self):
        self._accuracy_log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._accuracy_log_path.exists():
            with self._accuracy_log_path.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "timestamp",
                    "raw_transcribed_text",
                    "matched_command_category",
                    "confidence_score",
                    "success",
                ])

    def _log_accuracy_entry(
        self,
        raw_text: str,
        category: str | None,
        confidence: float,
        success: bool,
    ) -> None:
        try:
            with self._accuracy_log_path.open("a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    datetime.utcnow().isoformat(),
                    raw_text,
                    category or "",
                    f"{confidence:.4f}",
                    success,
                ])
        except Exception as exc:
            logger.exception("Failed to write accuracy log: %s", exc)

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for every audio block."""
        if status:
            logger.warning("Audio stream status: %s", status)
        try:
            # Convert cffi buffer to numpy array safely
            audio_np = np.frombuffer(bytes(indata), dtype=np.int16).copy()
            filtered = self.noise_filter.apply(audio_np)
            # Don't block if queue is full - drop the frame
            self._audio_queue.put_nowait(bytes(filtered))
        except queue.Full:
            pass  # drop frame to prevent overflow
        except Exception as e:
            logger.debug("Audio callback error: %s", e)

    def _listen_loop(self):
        """Main loop: reads audio queue -> ASR -> dispatch."""
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            dtype="int16",
            channels=1,
            latency="high",
            callback=self._audio_callback,
        ):
            logger.info(
                "Audio stream open (SR=%d, block=%d)", SAMPLE_RATE, BLOCK_SIZE
            )
            wake_active = False

            while self._running:
                try:
                    data = self._audio_queue.get(timeout=1)
                except queue.Empty:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text   = result.get("text", "").strip().lower()
                    conf   = self._mean_confidence(result)

                    if not text:
                        continue

                    logger.info("Heard: '%s' (confidence=%.2f)", text, conf)

                    # --- Wake-word gate ---
                    if not wake_active:
                        if any(w in text for w in WAKE_WORDS):
                            wake_active = True
                            self.feedback.chime()
                            logger.info("Wake word detected - listening for command...")
                        else:
                            logger.debug("Waiting for wake word, heard: '%s'", text)
                        continue

                    # --- Command processing ---
                    if conf >= CONFIDENCE_THRESHOLD:
                        self.total_commands += 1
                        logger.info("Processing command: '%s'", text)
                        handled, category = self.dispatcher.dispatch(text)
                        if handled:
                            self.matched_commands += 1
                            self.feedback.success()
                            logger.info("Command handled successfully")
                        else:
                            logger.info("No handler matched: '%s'", text)
                            self.feedback.error()
                        self._log_accuracy_entry(text, category, conf, handled)
                    else:
                        logger.info(
                            "Low confidence (%.2f) - ignored: '%s'", conf, text
                        )
                        self._log_accuracy_entry(text, None, conf, False)

                    wake_active = False  # require wake word again

                else:
                    # Partial result - log for debugging
                    partial = json.loads(self.recognizer.PartialResult())
                    partial_text = partial.get("partial", "")
                    if partial_text:
                        logger.debug("Partial: '%s'", partial_text)

    @staticmethod
    def _mean_confidence(result: dict) -> float:
        """Extract mean word confidence from Vosk result JSON."""
        words = result.get("result", [])
        if not words:
            return 1.0
        return sum(w.get("conf", 1.0) for w in words) / len(words)

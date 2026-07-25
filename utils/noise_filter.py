"""
NoiseFilter: Pre-processing pipeline to improve Vosk recognition accuracy.
Applies spectral subtraction + energy-based VAD before passing audio to ASR.
This is a key contributor to achieving 90%+ command accuracy.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

NOISE_FLOOR_FRAMES  = 20     # estimate noise from first N frames
ENERGY_THRESHOLD    = 0.01   # frames below this are treated as silence


class NoiseFilter:
    """
    Lightweight, CPU-efficient noise filter for 16-bit mono PCM audio.
    Two-stage pipeline:
      1. Adaptive noise floor estimation (spectral subtraction lite)
      2. Energy-based Voice Activity Detection (VAD) gating
    """

    def __init__(self):
        self._noise_profile: np.ndarray | None = None
        self._frame_count = 0
        self._alpha = 0.98    # smoothing factor for noise estimate

    def apply(self, raw: np.ndarray) -> np.ndarray:
        """
        raw : numpy int16 array from sounddevice callback
        returns : filtered numpy int16 array (same shape)
        """
        # Convert to float for processing
        audio = raw.astype(np.float32) / 32768.0

        # --- Stage 1: Noise floor estimation & subtraction ---
        if self._frame_count < NOISE_FLOOR_FRAMES:
            # Accumulate noise during silence at startup
            if self._noise_profile is None:
                self._noise_profile = np.abs(audio)
            else:
                self._noise_profile = (
                    self._alpha * self._noise_profile
                    + (1 - self._alpha) * np.abs(audio)
                )
            self._frame_count += 1
            # Return zeros during initial calibration
            return np.zeros_like(raw, dtype=np.int16)

        # Spectral subtraction (simplified, time-domain)
        subtracted = np.sign(audio) * np.maximum(np.abs(audio) - self._noise_profile, 0)

        # Update noise model slowly during quiet segments
        energy = np.mean(audio ** 2)
        if energy < ENERGY_THRESHOLD:
            self._noise_profile = (
                self._alpha * self._noise_profile
                + (1 - self._alpha) * np.abs(audio)
            )
            # Gate silence → return zeros (Vosk handles silence well)
            return np.zeros_like(raw, dtype=np.int16)

        # --- Stage 2: Soft clip to avoid overflow ---
        clipped = np.tanh(subtracted * 2.0)

        # Convert back to int16
        out = (clipped * 32767).astype(np.int16)
        return out.reshape(raw.shape)

    def reset(self):
        """Call if the microphone or ambient noise changes significantly."""
        self._noise_profile = None
        self._frame_count   = 0
        logger.info("NoiseFilter reset – recalibrating noise floor…")

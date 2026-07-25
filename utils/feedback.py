"""
AudioFeedback: Non-blocking beep/chime feedback so the user knows
the assistant heard them or encountered an error.
"""

import platform
import subprocess
import threading
import logging

logger = logging.getLogger(__name__)
OS = platform.system().lower()


class AudioFeedback:
    """
    Platform-agnostic audio cues:
      chime()   – wake-word detected, ready for command
      success() – command executed successfully
      error()   – command not recognised / execution failed
    """

    def chime(self):
        """Double-beep: assistant is awake."""
        self._play_async(self._chime)

    def success(self):
        """Single high beep: command succeeded."""
        self._play_async(self._success)

    def error(self):
        """Low-pitch beep: not understood."""
        self._play_async(self._error)

    # ------------------------------------------------------------------ #

    def _play_async(self, fn):
        threading.Thread(target=fn, daemon=True).start()

    def _chime(self):
        try:
            if OS == "windows":
                import winsound
                winsound.Beep(880, 120)
                winsound.Beep(1100, 120)
            elif OS == "darwin":
                subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"], capture_output=True)
            else:
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"], capture_output=True)
        except Exception as exc:
            logger.debug("AudioFeedback chime error: %s", exc)

    def _success(self):
        try:
            if OS == "windows":
                import winsound
                winsound.Beep(1200, 80)
            elif OS == "darwin":
                subprocess.run(["afplay", "/System/Library/Sounds/Pop.aiff"], capture_output=True)
            else:
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"], capture_output=True)
        except Exception as exc:
            logger.debug("AudioFeedback success error: %s", exc)

    def _error(self):
        try:
            if OS == "windows":
                import winsound
                winsound.Beep(400, 200)
            elif OS == "darwin":
                subprocess.run(["afplay", "/System/Library/Sounds/Basso.aiff"], capture_output=True)
            else:
                subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/dialog-error.oga"], capture_output=True)
        except Exception as exc:
            logger.debug("AudioFeedback error: %s", exc)

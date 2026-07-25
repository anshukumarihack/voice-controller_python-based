"""
Category 4 – System Control
Triggers: volume up/down/mute, brightness, shutdown, restart, sleep, lock
"""

import platform
import subprocess
import logging
import pyautogui
from commands.base import BaseCommand

logger = logging.getLogger(__name__)
OS = platform.system().lower()


class SystemControlCommand(BaseCommand):
    name = "SystemControl"
    keywords = [
        "volume up", "volume down", "mute", "unmute",
        "increase volume", "decrease volume", "set volume",
        "brightness up", "brightness down",
        "shutdown", "restart", "reboot", "sleep", "hibernate",
        "lock screen", "lock computer",
        "empty trash", "clear trash",
        "take screenshot",
    ]

    def execute(self, text: str) -> None:
        t = text.lower()

        # ── Volume ──────────────────────────────────────────────────────
        if "volume up" in t or "increase volume" in t or "louder" in t:
            self._volume_adjust(+10)
        elif "volume down" in t or "decrease volume" in t or "quieter" in t:
            self._volume_adjust(-10)
        elif "mute" in t and "unmute" not in t:
            self._mute()
        elif "unmute" in t:
            self._unmute()
        elif "set volume" in t:
            m = self.extract(r"set volume\s+(?:to\s+)?(\d+)", text)
            if m:
                self._set_volume(int(m.group(1)))

        # ── Brightness ──────────────────────────────────────────────────
        elif "brightness up" in t or "increase brightness" in t:
            self._brightness_adjust(+10)
        elif "brightness down" in t or "decrease brightness" in t:
            self._brightness_adjust(-10)

        # ── Power ───────────────────────────────────────────────────────
        elif "shutdown" in t or "shut down" in t:
            self._power_action("shutdown")
        elif "restart" in t or "reboot" in t:
            self._power_action("restart")
        elif "sleep" in t or "hibernate" in t:
            self._power_action("sleep")

        # ── Lock ────────────────────────────────────────────────────────
        elif "lock" in t:
            self._lock_screen()

    # ------------------------------------------------------------------ #

    def _volume_adjust(self, delta: int):
        key = "volumeup" if delta > 0 else "volumedown"
        steps = abs(delta) // 2
        for _ in range(steps):
            pyautogui.press(key)
        logger.info("Volume %s by %d", "up" if delta > 0 else "down", abs(delta))

    def _mute(self):
        pyautogui.press("volumemute")
        logger.info("Muted")

    def _unmute(self):
        pyautogui.press("volumemute")   # toggle
        logger.info("Unmuted")

    def _set_volume(self, level: int):
        """Set volume to a specific level (Linux/Windows/Mac)."""
        if OS == "linux":
            subprocess.run(["amixer", "sset", "Master", f"{level}%"], capture_output=True)
        elif OS == "darwin":
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
        elif OS == "windows":
            # Use nircmd if available, else skip
            subprocess.run(["nircmd", "setsysvolume", str(int(level / 100 * 65535))])
        logger.info("Volume set to %d%%", level)

    def _brightness_adjust(self, delta: int):
        if OS == "linux":
            subprocess.run(["brightnessctl", "set", f"{abs(delta)}%{'+'if delta>0 else '-'}"])
        elif OS == "darwin":
            step = 1 if delta > 0 else -1
            key = "brightness_up" if delta > 0 else "brightness_down"
            for _ in range(abs(delta) // 5):
                pyautogui.press(key)
        logger.info("Brightness %s", "up" if delta > 0 else "down")

    def _power_action(self, action: str):
        confirm = pyautogui.confirm(
            f"Are you sure you want to {action}?", "Voice Assistant"
        )
        if confirm != "OK":
            return
        if OS == "windows":
            cmds = {"shutdown": "shutdown /s /t 5", "restart": "shutdown /r /t 5", "sleep": "rundll32 powrprof.dll,SetSuspendState 0,1,0"}
        elif OS == "linux":
            cmds = {"shutdown": "shutdown -h now", "restart": "reboot", "sleep": "systemctl suspend"}
        else:
            cmds = {"shutdown": "shutdown -h now", "restart": "shutdown -r now", "sleep": "pmset sleepnow"}
        subprocess.run(cmds[action], shell=True)

    def _lock_screen(self):
        if OS == "windows":
            subprocess.run("rundll32 user32.dll,LockWorkStation", shell=True)
        elif OS == "linux":
            subprocess.run(["gnome-screensaver-command", "--lock"])
        elif OS == "darwin":
            subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
        logger.info("Screen locked")

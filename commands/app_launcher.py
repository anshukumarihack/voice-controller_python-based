"""
Category 1 – App Launcher
Triggers: "open <app>", "launch <app>", "start <app>"
"""

import subprocess
import platform
import logging
from commands.base import BaseCommand

logger = logging.getLogger(__name__)

# ── App name → executable map (cross-platform) ─────────────────────────────
APP_MAP = {
    # Browsers
    "chrome":       {"win": "chrome",          "linux": "google-chrome", "darwin": "open -a 'Google Chrome'"},
    "firefox":      {"win": "firefox",          "linux": "firefox",       "darwin": "open -a Firefox"},
    "edge":         {"win": "msedge",           "linux": "msedge",        "darwin": "open -a 'Microsoft Edge'"},
    # Dev tools
    "vs code":      {"win": "code",             "linux": "code",          "darwin": "code"},
    "terminal":     {"win": "cmd",              "linux": "x-terminal-emulator", "darwin": "open -a Terminal"},
    "notepad":      {"win": "notepad",          "linux": "gedit",         "darwin": "open -a TextEdit"},
    # Office
    "word":         {"win": "winword",          "linux": "libreoffice --writer", "darwin": "open -a 'Microsoft Word'"},
    "excel":        {"win": "excel",            "linux": "libreoffice --calc",   "darwin": "open -a 'Microsoft Excel'"},
    "powerpoint":   {"win": "powerpnt",         "linux": "libreoffice --impress","darwin": "open -a 'Microsoft PowerPoint'"},
    # Utilities
    "calculator":   {"win": "calc",             "linux": "gnome-calculator",     "darwin": "open -a Calculator"},
    "file manager": {"win": "explorer",         "linux": "nautilus",             "darwin": "open ~"},
    "task manager": {"win": "taskmgr",          "linux": "gnome-system-monitor", "darwin": "open -a 'Activity Monitor'"},
    "spotify":      {"win": "spotify",          "linux": "spotify",              "darwin": "open -a Spotify"},
    "slack":        {"win": "slack",            "linux": "slack",                "darwin": "open -a Slack"},
    "zoom":         {"win": "zoom",             "linux": "zoom",                 "darwin": "open -a zoom.us"},
    "discord":      {"win": "discord",          "linux": "discord",              "darwin": "open -a Discord"},
}

OS = platform.system().lower()   # 'windows' | 'linux' | 'darwin'


class AppLauncherCommand(BaseCommand):
    name = "AppLauncher"
    keywords = ["open ", "launch ", "start "]

    def can_handle(self, text: str) -> bool:
        text_lower = text.lower()
        return any(text_lower.startswith(kw) or f" {kw}" in text_lower for kw in self.keywords)

    def execute(self, text: str) -> None:
        app_name = self._extract_app_name(text)
        cmd = self._resolve_command(app_name)

        logger.info("Launching app: '%s' → command: '%s'", app_name, cmd)
        if OS == "windows":
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.DETACHED_PROCESS)
        else:
            subprocess.Popen(cmd, shell=True, start_new_session=True)

    def _extract_app_name(self, text: str) -> str:
        """Strip the trigger verb to get the app name."""
        for trigger in ["open ", "launch ", "start "]:
            idx = text.lower().find(trigger)
            if idx != -1:
                return text[idx + len(trigger):].strip()
        return text.strip()

    def _resolve_command(self, app_name: str) -> str:
        app_lower = app_name.lower()
        # Exact match first
        for key, cmds in APP_MAP.items():
            if key == app_lower:
                return cmds.get(OS, cmds.get("linux", key))
        # Partial match
        for key, cmds in APP_MAP.items():
            if key in app_lower or app_lower in key:
                return cmds.get(OS, cmds.get("linux", key))
        # Fallback: just try the name directly
        return app_name

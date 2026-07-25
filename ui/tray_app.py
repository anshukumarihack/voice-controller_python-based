"""
AssistantTrayApp: Minimal system-tray icon so users can
toggle listening, view stats, and quit — without a heavy GUI.
Requires: pystray, Pillow
"""

import threading
import logging
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

try:
    import pystray
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False
    logger.warning("pystray not installed – running headless (no tray icon)")


def _make_icon(active: bool) -> Image.Image:
    """Draw a simple mic icon (green=active, grey=paused)."""
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (60, 200, 80) if active else (140, 140, 140)
    # Mic body
    draw.ellipse([20, 4, 44, 36], fill=color)
    # Mic stand
    draw.rectangle([30, 36, 34, 52], fill=color)
    draw.ellipse([20, 50, 44, 58], fill=color)
    return img


class AssistantTrayApp:
    def __init__(self, assistant):
        self.assistant = assistant
        self._icon     = None

    def run(self):
        self.assistant.start()

        if not PYSTRAY_AVAILABLE:
            logger.info("Headless mode – press Ctrl-C to quit.")
            import time
            while True:
                time.sleep(1)
            return

        def on_toggle(icon, item):
            active = self.assistant.toggle_listening()
            icon.icon = _make_icon(active)
            icon.title = f"Voice Assistant ({'active' if active else 'paused'})"

        def on_stats(icon, item):
            import pyautogui
            acc = self.assistant.accuracy * 100
            total = self.assistant.total_commands
            pyautogui.alert(
                f"Commands processed : {total}\n"
                f"Recognition accuracy: {acc:.1f}%",
                "Voice Assistant Stats"
            )

        def on_quit(icon, item):
            self.assistant.stop()
            icon.stop()

        menu = pystray.Menu(
            pystray.MenuItem("Toggle Listening", on_toggle, default=True),
            pystray.MenuItem("Show Stats",       on_stats),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit",             on_quit),
        )

        self._icon = pystray.Icon(
            "voice_assistant",
            icon=_make_icon(True),
            title="Voice Assistant (active)",
            menu=menu,
        )
        self._icon.run()

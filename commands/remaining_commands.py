"""
Categories 5-11: Media, Window, Clipboard, Screenshot, Typing, Calendar, Calculator
"""

import re
import time
import datetime
import subprocess
import platform
import webbrowser
import logging
import pyautogui
import pyperclip
from commands.base import BaseCommand

logger = logging.getLogger(__name__)
OS = platform.system().lower()


# ═══════════════════════════════════════════════════════════════════════════
# Category 5 – Media Control
# ═══════════════════════════════════════════════════════════════════════════

class MediaControlCommand(BaseCommand):
    name = "MediaControl"
    keywords = [
        "play", "pause", "stop", "next song", "previous song",
        "next track", "previous track", "skip song", "skip track",
        "fast forward", "rewind",
    ]

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        # Avoid clashing with "play on youtube" (handled by WebSearch)
        if "youtube" in t:
            return False
        return super().can_handle(t)

    def execute(self, text: str) -> None:
        t = text.lower()
        if "next" in t or "skip" in t:
            pyautogui.press("nexttrack")
        elif "previous" in t or "prev" in t or "back" in t:
            pyautogui.press("prevtrack")
        elif "pause" in t or "play" in t:
            pyautogui.press("playpause")
        elif "stop" in t:
            pyautogui.press("stop")
        elif "fast forward" in t:
            pyautogui.hotkey("shift", "right")
        elif "rewind" in t:
            pyautogui.hotkey("shift", "left")
        logger.info("Media control: %s", text)


# ═══════════════════════════════════════════════════════════════════════════
# Category 6 – Window Manager
# ═══════════════════════════════════════════════════════════════════════════

class WindowManagerCommand(BaseCommand):
    name = "WindowManager"
    keywords = [
        "minimize", "maximise", "maximize", "restore window",
        "close window", "close tab",
        "switch window", "switch tab", "next tab", "previous tab",
        "new tab", "open tab",
        "alt tab", "task switcher",
    ]

    def execute(self, text: str) -> None:
        t = text.lower()
        if "minimize" in t:
            pyautogui.hotkey("win" if OS == "windows" else "super", "down") if OS != "darwin" else pyautogui.hotkey("ctrl", "m")
        elif "maximize" in t or "maximise" in t:
            pyautogui.hotkey("win" if OS == "windows" else "super", "up") if OS != "darwin" else pyautogui.hotkey("ctrl", "alt", "f")
        elif "close window" in t:
            pyautogui.hotkey("alt", "f4") if OS == "windows" else pyautogui.hotkey("cmd" if OS == "darwin" else "ctrl", "w")
        elif "close tab" in t:
            pyautogui.hotkey("ctrl", "w")
        elif "new tab" in t or "open tab" in t:
            pyautogui.hotkey("ctrl", "t")
        elif "next tab" in t:
            pyautogui.hotkey("ctrl", "tab")
        elif "previous tab" in t:
            pyautogui.hotkey("ctrl", "shift", "tab")
        elif "switch window" in t or "alt tab" in t:
            pyautogui.hotkey("alt", "tab")
        logger.info("Window action: %s", text)


# ═══════════════════════════════════════════════════════════════════════════
# Category 7 – Clipboard Operations
# ═══════════════════════════════════════════════════════════════════════════

class ClipboardCommand(BaseCommand):
    name = "Clipboard"
    keywords = [
        "copy", "paste", "cut", "select all",
        "undo", "redo",
        "show clipboard", "read clipboard", "what is in the clipboard",
    ]

    def can_handle(self, text: str) -> bool:
        t = text.lower()
        # Simple words like 'copy file' are handled by FileOps
        if "file" in t or "folder" in t:
            return False
        return super().can_handle(t)

    def execute(self, text: str) -> None:
        t = text.lower()
        mod = "cmd" if OS == "darwin" else "ctrl"
        if "select all" in t:
            pyautogui.hotkey(mod, "a")
        elif "copy" in t:
            pyautogui.hotkey(mod, "c")
        elif "cut" in t:
            pyautogui.hotkey(mod, "x")
        elif "paste" in t:
            pyautogui.hotkey(mod, "v")
        elif "undo" in t:
            pyautogui.hotkey(mod, "z")
        elif "redo" in t:
            pyautogui.hotkey(mod, "y") if OS == "windows" else pyautogui.hotkey(mod, "shift", "z")
        elif "clipboard" in t or "read clipboard" in t:
            content = pyperclip.paste()
            pyautogui.alert(f"Clipboard:\n{content[:300]}", "Voice Assistant")
        logger.info("Clipboard: %s", text)


# ═══════════════════════════════════════════════════════════════════════════
# Category 8 – Screenshot
# ═══════════════════════════════════════════════════════════════════════════

class ScreenshotCommand(BaseCommand):
    name = "Screenshot"
    keywords = [
        "take a screenshot", "take screenshot", "capture screen",
        "screenshot", "screen capture", "print screen",
    ]

    def execute(self, text: str) -> None:
        ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path  = f"screenshot_{ts}.png"
        time.sleep(0.5)   # brief pause so any popup clears
        img = pyautogui.screenshot()
        img.save(path)
        logger.info("Screenshot saved: %s", path)
        pyautogui.alert(f"Screenshot saved:\n{path}", "Voice Assistant")


# ═══════════════════════════════════════════════════════════════════════════
# Category 9 – Typing / Text Input
# ═══════════════════════════════════════════════════════════════════════════

class TypingCommand(BaseCommand):
    name = "Typing"
    keywords = [
        "type ", "write ", "input text",
        "press enter", "press tab", "press escape", "press backspace",
        "press delete", "press space",
    ]

    def execute(self, text: str) -> None:
        t = text.lower()
        if "press enter" in t:
            pyautogui.press("enter")
        elif "press tab" in t:
            pyautogui.press("tab")
        elif "press escape" in t or "press esc" in t:
            pyautogui.press("escape")
        elif "press backspace" in t:
            pyautogui.press("backspace")
        elif "press delete" in t:
            pyautogui.press("delete")
        elif "press space" in t:
            pyautogui.press("space")
        elif t.startswith("type ") or t.startswith("write "):
            content = re.sub(r"^(type|write)\s+", "", t, flags=re.IGNORECASE).strip()
            pyautogui.typewrite(content, interval=0.05)
        logger.info("Typing/key action: %s", text)


# ═══════════════════════════════════════════════════════════════════════════
# Category 10 – Calendar / Time
# ═══════════════════════════════════════════════════════════════════════════

class CalendarCommand(BaseCommand):
    name = "Calendar"
    keywords = [
        "what time is it", "what is the time",
        "what day is it", "what is today",
        "what is the date", "today's date",
        "set alarm", "set timer", "set reminder",
        "open calendar",
    ]

    def execute(self, text: str) -> None:
        t = text.lower()
        now = datetime.datetime.now()

        if "time" in t and ("what" in t or "tell me" in t):
            msg = now.strftime("The current time is %I:%M %p")
            pyautogui.alert(msg, "Voice Assistant")
            logger.info(msg)

        elif "date" in t or "today" in t or "day" in t:
            msg = now.strftime("Today is %A, %B %d, %Y")
            pyautogui.alert(msg, "Voice Assistant")
            logger.info(msg)

        elif "timer" in t:
            m = self.extract(r"(\d+)\s*(second|minute|hour)", text)
            if m:
                n, unit = int(m.group(1)), m.group(2)
                secs = n * {"second": 1, "minute": 60, "hour": 3600}[unit]
                logger.info("Timer set for %d seconds", secs)
                threading = __import__("threading")
                def _ring():
                    time.sleep(secs)
                    pyautogui.alert(f"⏰ Timer finished! ({n} {unit}{'s' if n>1 else ''})", "Voice Assistant")
                threading.Thread(target=_ring, daemon=True).start()

        elif "open calendar" in t:
            if OS == "darwin":
                subprocess.Popen(["open", "-a", "Calendar"])
            elif OS == "windows":
                subprocess.Popen(["start", "outlookcal:"], shell=True)
            else:
                webbrowser.open("https://calendar.google.com")


# ═══════════════════════════════════════════════════════════════════════════
# Category 11 – Calculator
# ═══════════════════════════════════════════════════════════════════════════

class CalculatorCommand(BaseCommand):
    name = "Calculator"
    keywords = [
        "calculate", "what is", "compute", "solve",
        "plus", "minus", "times", "divided by", "multiplied by",
    ]
    patterns = [
        r"\d+\s*(?:plus|minus|times|divided\s+by|multiplied\s+by|\+|\-|\*|\/)\s*\d+",
    ]

    def execute(self, text: str) -> None:
        t = text.lower()

        # Normalise spoken math to symbols
        expr = (t
            .replace("what is", "").replace("calculate", "").replace("compute", "")
            .replace("plus", "+").replace("minus", "-")
            .replace("times", "*").replace("multiplied by", "*")
            .replace("divided by", "/").strip()
        )

        # Extract numeric expression
        m = re.search(r"[\d\s\+\-\*\/\.\(\)]+", expr)
        if not m:
            if "open calculator" in t or "calculator" in t:
                # Just launch the app
                if OS == "windows":
                    subprocess.Popen("calc", shell=True)
                elif OS == "darwin":
                    subprocess.Popen(["open", "-a", "Calculator"])
                else:
                    subprocess.Popen(["gnome-calculator"])
            return

        try:
            result = eval(m.group().strip())   # safe: only digits and operators
            msg = f"{m.group().strip()} = {result}"
            logger.info("Calculator: %s", msg)
            pyautogui.alert(msg, "Voice Assistant")
        except Exception as exc:
            logger.warning("Calculator error: %s", exc)

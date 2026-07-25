"""
Category 2 – File Operations
Triggers: create file, delete file, move file, open folder, rename file
Uses PyAutoGUI + OS-level calls for safe automation
"""

import os
import shutil
import subprocess
import platform
import logging
import pyautogui
from pathlib import Path
from commands.base import BaseCommand

logger = logging.getLogger(__name__)

HOME = Path.home()
OS   = platform.system().lower()


class FileOpsCommand(BaseCommand):
    name = "FileOps"
    keywords = [
        "create file", "new file",
        "delete file", "remove file",
        "open folder", "open directory",
        "rename file",
        "copy file",
        "move file",
    ]
    patterns = [
        r"(create|make|new)\s+(a\s+)?file\s+(?P<name>\S+)",
        r"delete\s+(file\s+)?(?P<name>\S+)",
        r"open\s+(folder|directory)\s+(?P<path>.+)",
        r"rename\s+(?P<old>\S+)\s+to\s+(?P<new>\S+)",
    ]

    def execute(self, text: str) -> None:
        text_lower = text.lower()

        if "create file" in text_lower or "new file" in text_lower or "make file" in text_lower:
            self._create_file(text)

        elif "delete file" in text_lower or "remove file" in text_lower:
            self._delete_file(text)

        elif "open folder" in text_lower or "open directory" in text_lower:
            self._open_folder(text)

        elif "rename" in text_lower:
            self._rename_file(text)

        elif "copy file" in text_lower:
            self._copy_file(text)

        elif "move file" in text_lower:
            self._move_file(text)

    # ------------------------------------------------------------------ #
    #  Handlers                                                            #
    # ------------------------------------------------------------------ #

    def _create_file(self, text: str):
        m = self.extract(r"(create|make|new)\s+(?:a\s+)?file\s+(?:named?\s+)?(?P<name>\S+)", text)
        name = m.group("name") if m else "new_file.txt"
        path = HOME / "Desktop" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        logger.info("Created file: %s", path)
        pyautogui.alert(f"File created:\n{path}", "Voice Assistant")

    def _delete_file(self, text: str):
        m = self.extract(r"(delete|remove)\s+(?:file\s+)?(?P<name>\S+)", text)
        if not m:
            return
        name = m.group("name")
        path = HOME / "Desktop" / name
        if path.exists():
            path.unlink()
            logger.info("Deleted file: %s", path)
            pyautogui.alert(f"Deleted:\n{path}", "Voice Assistant")
        else:
            logger.warning("File not found: %s", path)
            pyautogui.alert(f"File not found:\n{path}", "Voice Assistant")

    def _open_folder(self, text: str):
        m = self.extract(r"open\s+(?:folder|directory)\s+(?P<path>.+)", text)
        folder = m.group("path").strip() if m else str(HOME)
        path = Path(folder).expanduser()
        if OS == "windows":
            subprocess.Popen(["explorer", str(path)])
        elif OS == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
        logger.info("Opened folder: %s", path)

    def _rename_file(self, text: str):
        m = self.extract(r"rename\s+(?P<old>\S+)\s+to\s+(?P<new>\S+)", text)
        if not m:
            return
        old_path = HOME / "Desktop" / m.group("old")
        new_path = HOME / "Desktop" / m.group("new")
        if old_path.exists():
            old_path.rename(new_path)
            logger.info("Renamed %s → %s", old_path, new_path)
        else:
            logger.warning("Source not found: %s", old_path)

    def _copy_file(self, text: str):
        m = self.extract(r"copy\s+(?:file\s+)?(?P<src>\S+)\s+to\s+(?P<dst>\S+)", text)
        if not m:
            return
        src = Path(m.group("src")).expanduser()
        dst = Path(m.group("dst")).expanduser()
        shutil.copy2(str(src), str(dst))
        logger.info("Copied %s → %s", src, dst)

    def _move_file(self, text: str):
        m = self.extract(r"move\s+(?:file\s+)?(?P<src>\S+)\s+to\s+(?P<dst>\S+)", text)
        if not m:
            return
        src = Path(m.group("src")).expanduser()
        dst = Path(m.group("dst")).expanduser()
        shutil.move(str(src), str(dst))
        logger.info("Moved %s → %s", src, dst)

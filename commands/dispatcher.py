"""
CommandDispatcher: Routes ASR text to the correct command handler.
Supports 10+ command categories with keyword/regex matching.
"""

import re
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """
    Match voice command text → handler function.
    Priority order: exact phrase → prefix → regex → fuzzy fallback.
    """

    def __init__(self):
        # Import all category handlers
        from commands.app_launcher   import AppLauncherCommand
        from commands.file_ops       import FileOpsCommand
        from commands.web_search     import WebSearchCommand
        from commands.system_control import SystemControlCommand
        from commands.media_control  import MediaControlCommand
        from commands.window_manager import WindowManagerCommand
        from commands.clipboard_ops  import ClipboardCommand
        from commands.screenshot     import ScreenshotCommand
        from commands.typing_cmd     import TypingCommand
        from commands.calendar_cmd   import CalendarCommand
        from commands.calculator     import CalculatorCommand

        # Instantiate all handlers
        self._handlers = [
            AppLauncherCommand(),
            FileOpsCommand(),
            WebSearchCommand(),
            SystemControlCommand(),
            MediaControlCommand(),
            WindowManagerCommand(),
            ClipboardCommand(),
            ScreenshotCommand(),
            TypingCommand(),
            CalendarCommand(),
            CalculatorCommand(),
        ]

        logger.info(
            "CommandDispatcher ready – %d handler categories loaded",
            len(self._handlers)
        )

    def dispatch(self, text: str) -> tuple[bool, str | None]:
        """
        Try each handler in order. Return a tuple of (handled, command category).
        """
        for handler in self._handlers:
            if handler.can_handle(text):
                logger.info("[%s] handling: '%s'", handler.name, text)
                try:
                    handler.execute(text)
                    return True, handler.name
                except Exception as exc:
                    logger.exception("[%s] error: %s", handler.name, exc)
                    return False, handler.name
        return False, None

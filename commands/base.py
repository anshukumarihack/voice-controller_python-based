"""Base class for all voice command handlers."""

import re
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    Every command category subclasses this.
    Provides keyword matching helpers so handlers stay declarative.
    """

    name: str = "base"
    keywords: list[str] = []          # simple substring triggers
    patterns: list[str] = []          # regex triggers (compiled on init)

    def __init__(self):
        self._compiled = [re.compile(p, re.IGNORECASE) for p in self.patterns]

    # ------------------------------------------------------------------ #
    #  Override in subclasses                                              #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def execute(self, text: str) -> None:
        """Perform the action. Raise on failure."""

    # ------------------------------------------------------------------ #
    #  Matching logic (usually no need to override)                        #
    # ------------------------------------------------------------------ #

    def can_handle(self, text: str) -> bool:
        text_lower = text.lower()
        if any(kw in text_lower for kw in self.keywords):
            return True
        return any(p.search(text) for p in self._compiled)

    # ------------------------------------------------------------------ #
    #  Convenience                                                         #
    # ------------------------------------------------------------------ #

    def extract(self, pattern: str, text: str) -> re.Match | None:
        return re.search(pattern, text, re.IGNORECASE)

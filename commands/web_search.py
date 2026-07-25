"""
Category 3 – Web Search
Triggers: "search for <query>", "google <query>", "look up <query>",
          "youtube <query>", "wikipedia <query>", "weather in <city>"
"""

import webbrowser
import urllib.parse
import logging
from commands.base import BaseCommand

logger = logging.getLogger(__name__)

SEARCH_ENGINES = {
    "google":    "https://www.google.com/search?q={}",
    "youtube":   "https://www.youtube.com/results?search_query={}",
    "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search={}",
    "github":    "https://github.com/search?q={}",
    "maps":      "https://www.google.com/maps/search/{}",
}


class WebSearchCommand(BaseCommand):
    name = "WebSearch"
    keywords = [
        "search for", "search ",
        "google ", "look up",
        "find information",
        "youtube ", "play on youtube",
        "wikipedia ",
        "weather in", "weather for",
        "maps ", "directions to",
        "open website", "go to website",
    ]

    def execute(self, text: str) -> None:
        text_lower = text.lower()

        # YouTube
        if "youtube" in text_lower or "play on youtube" in text_lower:
            query = self._strip(text_lower, ["youtube", "play on youtube", "search", "for"])
            self._open(SEARCH_ENGINES["youtube"], query)

        # Wikipedia
        elif "wikipedia" in text_lower:
            query = self._strip(text_lower, ["wikipedia", "search", "for", "on"])
            self._open(SEARCH_ENGINES["wikipedia"], query)

        # Weather
        elif "weather" in text_lower:
            m = self.extract(r"weather\s+(?:in|for)\s+(.+)", text)
            city = m.group(1).strip() if m else "current location"
            self._open("https://www.google.com/search?q=weather+{}", city)

        # Maps / directions
        elif "maps" in text_lower or "directions to" in text_lower:
            m = self.extract(r"(?:maps|directions\s+to)\s+(.+)", text)
            dest = m.group(1).strip() if m else ""
            self._open(SEARCH_ENGINES["maps"], dest)

        # Open a website directly
        elif "open website" in text_lower or "go to" in text_lower:
            m = self.extract(r"(?:open website|go to)\s+(.+)", text)
            site = m.group(1).strip() if m else ""
            if not site.startswith("http"):
                site = "https://" + site
            webbrowser.open(site)
            logger.info("Opened URL: %s", site)

        # Default Google search
        else:
            query = self._strip(text_lower, ["search for", "search", "google", "look up", "find information about", "find"])
            self._open(SEARCH_ENGINES["google"], query)

    def _open(self, url_template: str, query: str):
        encoded = urllib.parse.quote_plus(query)
        url = url_template.format(encoded)
        webbrowser.open(url)
        logger.info("Web search: '%s' → %s", query, url)

    @staticmethod
    def _strip(text: str, prefixes: list[str]) -> str:
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix):].strip()
        # Try removing any prefix found anywhere
        for prefix in prefixes:
            if prefix in text:
                return text[text.index(prefix) + len(prefix):].strip()
        return text.strip()

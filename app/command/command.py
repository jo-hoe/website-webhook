
from abc import ABC, abstractmethod

from app.scraper import Scraper
from app.templating import PLACEHOLDER_END, PLACEHOLDER_START, template

PLACEHOLDER_COMMANDS_PREFIX = "commands."


class Command(ABC):

    def __init__(self, kind: str, name: str, url: str, scraper: Scraper) -> None:
        self._kind = kind
        self._name = name
        self._url = url
        self._scraper = scraper

    @abstractmethod
    def execute(self) -> bool:
        pass

    def replace_placeholder(self, input: str) -> str:
        result = input

        result = template("kind", result, self._kind)
        result = template("url", result, self._url)
        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.name", result, self._name)

        return result

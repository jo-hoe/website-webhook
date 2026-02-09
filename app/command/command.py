from abc import ABC, abstractmethod

from app.scraper.scraper import Scraper
from app.templating import template

PLACEHOLDER_COMMANDS_PREFIX = "commands."


class Command(ABC):
    """
    Command lifecycle contract (all commands MUST implement):
    - execute() -> bool

    Implementation guidelines:
    - Do NOT write to persistent storage in execute(); only stage pending values.
    - Use replace_placeholder() to expose both baseline and pending values so the
      callback body/headers reflect the intended state transition.
    """

    def __init__(self, kind: str, name: str, url: str, scraper: Scraper) -> None:
        self._kind = kind
        self._name = name
        self._url = url
        self._scraper = scraper

    @abstractmethod
    def execute(self) -> bool:
        """
        Detect changes and stage pending state (no persistence). Return True if a callback is needed.
        """
        pass


    def replace_placeholder(self, input: str) -> str:
        result = input

        result = template("kind", result, self._kind)
        result = template("url", result, self._url)
        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.name", result, self._name)

        return result
    
    @property
    def name(self) -> str:
        return self._name


class CommandException(Exception):
    pass

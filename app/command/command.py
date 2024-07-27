
from abc import ABC, abstractmethod

from app.templating import PLACEHOLDER_END, PLACEHOLDER_START, template

PLACEHOLDER_COMMANDS_PREFIX = "commands."


class Command(ABC):

    def __init__(self, kind: str, name: str, url: str) -> None:
        self.kind = kind
        self.name = name
        self.url = url

    @abstractmethod
    def execute(self) -> bool:
        pass

    def replace_placeholder(self, input: str) -> str:
        result = input

        result = template("kind", result, self.kind)
        result = template("url", result, self.url)
        result = template("name", result, self.name)

        return result


from abc import ABC, abstractmethod

PLACEHOLDER_COMMANDS_PREFIX = "commands."

class Command(ABC):

    def __init__(self, kind: str, name: str) -> None:
        self.kind = kind
        self.name = name

    @abstractmethod
    def execute(self, url: str) -> bool:
        pass

    def replace_placeholder(self, input: str) -> str:
        pass

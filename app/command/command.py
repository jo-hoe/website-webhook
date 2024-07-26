
from abc import ABC, abstractmethod


class Command(ABC):

    @abstractmethod
    def execute(self) -> bool:
        pass

    @abstractmethod
    def template(self, input: str) -> str:
        pass

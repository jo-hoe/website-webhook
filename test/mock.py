from typing import List
from app.command.command import Command
from app.scraper import Scraper


class MockScraper(Scraper):

    def __init__(self, result_values: List[str] = ["mock"]) -> None:
        self._result_values = result_values
        self._index = 0

    def scrape(self, url: str, xpath: str) -> str:
        result = self._result_values[self._index % len(self._result_values)]
        self._index += 1
        return result


class MockCommand(Command):

    KIND = "mockCommand"

    def __init__(self, name: str = "mock", url: str = "", scraper: Scraper = MockScraper(), return_values: List[bool] = [True], raise_exception: bool = False) -> None:
        super().__init__(self.KIND, name, url, scraper)
        self._return_values = return_values
        self._index = 0
        self.raise_exception = raise_exception

    def execute(self) -> bool:
        if self.raise_exception:
            raise Exception("Mock exception")

        result = self._return_values[self._index % len(self._return_values)]
        self._index += 1
        return result

    def replace_placeholder(self, input: str) -> str:
        return super().replace_placeholder(input)

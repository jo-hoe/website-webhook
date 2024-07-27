from typing import List
from app.command.command import Command
from app.scraper import Scraper


class MockScraper(Scraper):

    def __init__(self, result_values: List[str]) -> None:
        self._result_values = result_values
        self._index = 0

    def scrape(self, url: str, xpath: str) -> str:
        result = self._result_values[self._index % len(self._result_values)]
        self._index += 1
        return result


class MockCommand(Command):

    def __init__(self, kind: str, name: str, url: str, scraper: Scraper, return_values: List[bool] = [True]) -> None:
        super().__init__(kind, name, url, scraper)
        self._return_values = return_values
        self._index = 0

    def execute(self) -> bool:
        result = self._return_values[self._index % len(self._return_values)]
        self._index += 1
        return result

    def replace_placeholder(self, input: str) -> str:
        return super().replace_placeholder(input)

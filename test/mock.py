from enum import Enum
from typing import List
from app.command.command import Command
from app.scraper.scraper import Scraper
from lxml import etree


class MockScraper(Scraper):

    def __init__(self, result_values: List[str] = ["mock"]) -> None:
        self._result_values = result_values
        self._index = 0

    def scrape(self, url: str, xpath: str) -> str:
        result = self._result_values[self._index % len(self._result_values)]
        self._index += 1
        return result


class MockContentType(Enum):
    HTML = "html"
    XML = "xml"


class MockScraperFromFile(Scraper):

    ''' A mock scraper that reads content from a local file instead of making HTTP requests. '''

    def __init__(self, file_path: str, content_type: MockContentType) -> None:
        self._file_path = file_path
        self._content_type = content_type

    def scrape(self, url: str, xpath: str) -> str:
        file_content = ""
        with open(self._file_path, 'r') as file:
            file_content = file.read()

        if self._content_type == MockContentType.XML:
            tree = etree.XML(file_content)
        elif self._content_type == MockContentType.HTML:
            tree = etree.HTML(file_content)
        else:
            raise Exception(f"Unsupported content type: {self._content_type}")

        return self._find_element_in_tree(tree, xpath)


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

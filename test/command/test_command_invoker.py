import pytest
import responses
from typing import List

from app.config import Callback
from app.scraper import Scraper
from app.command.command import Command
from app.command.commandinvoker import CommandInvoker


class MockScraper(Scraper):

    def __init__(self, result_values: List[str]) -> None:
        self._result_values = result_values
        self._index = 0

    def scrape(self, url: str, xpath: str) -> str:
        result = self._result_values[self._index % len(self._result_values)]
        self._index += 1
        return result


class MockCommand(Command):
    def execute(self) -> bool:
        return True

    def replace_placeholder(self, input: str) -> str:
        return super().replace_placeholder(input)


@pytest.mark.integration_test
@responses.activate
def test_command_invoker():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'body': '{}',
        'status': 200,
        'content_type': 'application/json',
        'adding_headers': {'X-Foo': 'Bar'}
    })

    command = MockCommand("mock", "test-name", "test-url",
                          MockScraper(["a", "b"]))
    callback = Callback(
        url=callback_test_url,
        method=callback_test_method,
        retries=0,
        headers=[],
        body=[]
    )
    invoker = CommandInvoker([command], callback)

    assert invoker.execute_all_commands(), "execute_all_commands failed"

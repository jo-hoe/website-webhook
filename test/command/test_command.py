

from app.scraper import Scraper
from test.mock import MockCommand


def test_replace_placeholder():
    command = MockCommand("mock", "test-name", "test-url", Scraper())
    assert command.replace_placeholder(
        "<<kind>> <<commands.test-name.name>> <<url>>") == "mock test-name test-url", "replace_placeholder failed"



from app.scraper import Scraper
from test.mock import MockCommand


def test_replace_placeholder():
    command = MockCommand("test-name", "test-url", Scraper())
    assert command.replace_placeholder(
        "<<kind>> <<commands.test-name.name>> <<url>>") == f"{MockCommand.KIND} test-name test-url", "replace_placeholder failed"

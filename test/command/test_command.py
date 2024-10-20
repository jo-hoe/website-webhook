
from test.mock import MockCommand, MockScraper


def test_replace_placeholder():
    command = MockCommand("test-name", "test-url", MockScraper())
    assert command.replace_placeholder(
        "<<kind>> <<commands.test-name.name>> <<url>>") == f"{MockCommand.KIND} test-name test-url", "replace_placeholder failed"

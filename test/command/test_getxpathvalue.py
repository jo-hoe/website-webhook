from app.command.getxpathvalue import GetXPathValue
from test.mock import MockScraper


def test_replace_placeholder():
    command = GetXPathValue(
        "test-name", "", "", MockScraper(["a"]))

    # execute (no persistence needed for this command)
    assert command.execute() is False

    result = command.replace_placeholder(
        "<<commands.test-name.name>> <<commands.test-name.value>>")

    expected_result = "test-name a"
    error_msg = f"{result} did not match {expected_result}"
    assert expected_result == result, error_msg


def test_does_not_trigger_callback():
    command = GetXPathValue(
        "test-name", "", "", MockScraper(["a"]))

    assert command.execute() is False


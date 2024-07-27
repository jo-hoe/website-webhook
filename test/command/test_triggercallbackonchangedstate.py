
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from test.mock import MockScraper


def test_trigger():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper(["a", "a", "b", "b"]))

    assert not command.execute(), "expected result after first run is false"
    assert not command.execute(), "expected result after second run is false"
    assert command.execute(), "expected result after third run is true"

    assert not command.execute(), "should not find change"


def test_replace_placeholder():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper(["a", "b"]))

    command.execute()
    command.execute()

    result = command.replace_placeholder(
        "<<commands.test-name.name>> <<commands.test-name.old>> <<commands.test-name.new>>")

    expected_result = "test-name a b"
    error_msg = f"{result} did not match {expected_result}"
    assert expected_result == result, error_msg


from os import path
from pathlib import Path
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from test.mock import MockContentType, MockScraper, MockScraperFromFile

TEST_RESOURCES_DIR = path.join(
    Path(__file__).resolve().parent.parent, "resources")


def test_trigger():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper(["a", "a", "b", "b"]))

    assert not command.execute(), "expected result after first run is false"
    assert not command.execute(), "expected result after second run is false"
    assert command.execute(), "expected result after third run is true"

    assert not command.execute(), "should not find change"


def test_throw_exception_on_not_found():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None]))

    try:
        command.execute()
        assert False, "expected CommandException"
    except Exception as ex:
        assert isinstance(
            ex, Exception), f"expected CommandException, got {type(ex)}"
        
def test_trigger_first_no_element_then_element_appears():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None, None, "value"]), False)

    assert False == command.execute()  # First run, None, should not trigger
    assert False == command.execute()  # Second run, None, should not trigger
    assert command.execute(), "expected result after third run is true"


def test_suppress_exception_on_not_found():
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None]), exception_on_not_found=False)

    assert not command.execute()


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


def test_rss_feed_regex_first_item_in_list():
    test_file_path = path.join(TEST_RESOURCES_DIR, "test_feed_content.xml")

    command = TriggerCallbackOnChangedState(
        "test-name", "", "(//*[local-name()='link'][1]/@href)[2]", MockScraperFromFile(
            test_file_path, MockContentType.XML)
    )

    # First run establishes baseline; no change should be triggered
    assert not command.execute(), "expected result after first run is false"
    assert command._old_value is not None, "old value should be set"
    assert command._old_value == "https://example.test/watch?v=VID0001", "unexpected old value"


def test_rss_feed_regex_link_by_text():
    test_file_path = path.join(TEST_RESOURCES_DIR, "test_feed_content.xml")

    xpath = "(//*[local-name()='entry'][contains(./*[local-name()='title'], 'Donut of Doom Episode')])[1]/*[local-name()='link' and @rel='alternate']/@href"

    command = TriggerCallbackOnChangedState(
        "test-name", "", xpath, MockScraperFromFile(
            test_file_path, MockContentType.XML)
    )

    # First run establishes baseline; no change should be triggered
    assert not command.execute(), "expected result after first run is false"
    assert command._old_value is not None, "old value should be set"
    assert command._old_value == "https://example.test/watch?v=VID0008", "unexpected old value"

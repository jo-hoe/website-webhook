
from os import path
from pathlib import Path
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from app.storage.inmemory_storage import InMemoryStorage
from test.mock import MockContentType, MockScraper, MockScraperFromFile

TEST_RESOURCES_DIR = path.join(
    Path(__file__).resolve().parent.parent, "resources")


def test_trigger():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper(["a", "a", "b", "b"]), storage)

    # 1st run: establish baseline, no trigger
    assert command.execute() is False, "expected result after first run is false"
    command.commit_state()

    # 2nd run: same value, no trigger
    assert command.execute() is False, "expected result after second run is false"
    command.commit_state()

    # 3rd run: value changed, should trigger
    assert command.execute() is True, "expected result after third run is true"
    command.commit_state()

    # 4th run: no change, no trigger
    assert command.execute() is False, "should not find change"
    command.commit_state()


def test_throw_exception_on_not_found():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None]), storage)

    try:
        command.execute()
        assert False, "expected CommandException"
    except Exception as ex:
        assert isinstance(
            ex, Exception), f"expected CommandException, got {type(ex)}"
        
def test_trigger_first_no_element_then_element_appears():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None, None, "value"]), storage, False)

    assert command.execute() is False  # First run, None, should not trigger
    command.commit_state()
    assert command.execute() is False  # Second run, None, should not trigger
    command.commit_state()
    assert command.execute() is True, "expected result after third run is true"
    command.commit_state()

def test_do_not_trigger_on_empty_or_none_values():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None, "", None, "", "value"]), storage, False)

    assert command.execute() is False  # None, should not trigger
    command.commit_state()
    assert command.execute() is False  # empty, should not trigger
    command.commit_state()
    assert command.execute() is False  # None, should not trigger
    command.commit_state()
    assert command.execute() is False  # empty, should not trigger
    command.commit_state()
    assert command.execute() is True, "expected result after value is set is true"
    command.commit_state()

def test_suppress_exception_on_not_found():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper([None]), storage, exception_on_not_found=False)

    assert command.execute() is False
    command.commit_state()


def test_replace_placeholder():
    storage = InMemoryStorage()
    command = TriggerCallbackOnChangedState(
        "test-name", "", "", MockScraper(["a", "b"]), storage)

    command.execute()
    command.commit_state()
    command.execute()
    command.commit_state()

    result = command.replace_placeholder(
        "<<commands.test-name.name>> <<commands.test-name.old>> <<commands.test-name.new>>")

    expected_result = "test-name a b"
    error_msg = f"{result} did not match {expected_result}"
    assert expected_result == result, error_msg


def test_rss_feed_regex_first_item_in_list():
    test_file_path = path.join(TEST_RESOURCES_DIR, "test_feed_content.xml")
    storage = InMemoryStorage()

    command = TriggerCallbackOnChangedState(
        "test-name", "", "(//*[local-name()='link'][1]/@href)[2]", MockScraperFromFile(
            test_file_path, MockContentType.XML), storage
    )

    # First run establishes baseline; no change should be triggered
    assert command.execute() is False, "expected result after first run is false"
    command.commit_state()
    assert command._get_state("previous") is not None, "previous value should be set"
    assert command._get_state("previous") == "https://example.test/watch?v=VID0001", "unexpected previous value"


def test_rss_feed_regex_link_by_text():
    test_file_path = path.join(TEST_RESOURCES_DIR, "test_feed_content.xml")
    storage = InMemoryStorage()

    xpath = "(//*[local-name()='entry'][contains(./*[local-name()='title'], 'Donut of Doom Episode')])[1]/*[local-name()='link' and @rel='alternate']/@href"

    command = TriggerCallbackOnChangedState(
        "test-name", "", xpath, MockScraperFromFile(
            test_file_path, MockContentType.XML), storage
    )

    # First run establishes baseline; no change should be triggered
    assert command.execute() is False, "expected result after first run is false"
    command.commit_state()
    assert command._get_state("previous") is not None, "previous value should be set"
    assert command._get_state("previous") == "https://example.test/watch?v=VID0008", "unexpected previous value"

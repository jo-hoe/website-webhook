
import re
import pytest
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState

TEST_URL = "https://pypi.org/project/cloudscraper/"
HEADER_XPATH = "//h1[@class='package-header__name']/text()"
PIP_INSTALL_COMMAND_XPATH = "//span[@id='pip-command']/text()"


@pytest.mark.integration_test
def test_trigger():
    command = TriggerCallbackOnChangedState(
        "test-name", TEST_URL, HEADER_XPATH)

    assert not command.execute(), "expected result after first run is false"
    assert not command.execute(), "expected result after second run is false"

    # changing xpath to enforce change
    command._xpath = PIP_INSTALL_COMMAND_XPATH
    assert command.execute(), "expected result after third run is true"
    assert not command.execute(), "should not find change"


@pytest.mark.integration_test
def test_replace_placeholder():
    command = TriggerCallbackOnChangedState(
        "test-name", TEST_URL, HEADER_XPATH)

    command.execute()
    command._xpath = PIP_INSTALL_COMMAND_XPATH
    command.execute()

    result = command.replace_placeholder(
        "<<commands.test-name.name>> <<commands.test-name.old>> <<commands.test-name.new>>")

    # result should be something like
    # test-name cloudscraper 1.2.71 pip install cloudscraper
    assert None != re.match("^test-name cloudscraper [0-9.]* pip install cloudscraper", result), f"{result} did not match expected value"

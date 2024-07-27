import os
import pathlib
from datetime import timedelta

from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from app.config import create_config
from app.scraper import Scraper

TEST_FILE_PATH = "test_config.yaml"


def test_create_config():
    config_file_path = get_configuration_filepath()
    config = create_config(config_file_path)

    # general
    assert config.interval == timedelta(minutes=4)
    assert config.url == "https://myurl.com"

    # callback
    assert config.callback.url == "https://example.com/callback"
    assert config.callback.method == "POST"
    assert config.callback.timeout == timedelta(seconds=24)
    assert config.callback.retries == 3
    # callback headers
    assert len(config.callback.headers) == 1
    assert config.callback.headers[0].name == "Content-Type"
    assert config.callback.headers[0].value == "application/json"
    # callback body
    assert len(config.callback.body) == 2
    assert config.callback.body[0].name == "event"
    assert config.callback.body[0].value == "some static string"
    assert config.callback.body[1].name == "description"
    assert config.callback.body[1].value == "The value on page <<url>> changed from '<<commands.changedState.old>>' to '<<commands.changedState.new>>'"

    # commands
    assert len(config.commands) == 1
    assert isinstance(config.commands[0], TriggerCallbackOnChangedState)
    assert config.commands[0]._kind == "triggerCallbackOnChangedState"
    assert config.commands[0]._name == "changedState"
    assert config.commands[0]._url == "https://myurl.com"
    assert config.commands[0]._xpath == "//a[@class='some class']/text()"
    assert isinstance(config.commands[0]._scraper, Scraper)


def get_configuration_filepath():
    test_dir = pathlib.Path(__file__).parent.resolve()
    return os.path.join(test_dir, "resources", TEST_FILE_PATH)

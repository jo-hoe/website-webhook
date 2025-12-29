from threading import Thread
from time import sleep
import pytest

from app.config import Callback, Config, StorageConfig
from app.websitewebhook import schedule_process
from test.mock import MockCommand


def mock_function(dummy=None):
    return True


@pytest.mark.integration_test
def test_schedule_process():
    config = Config(
        cron="*/1 * * * * *",
        execute_on_start=True,
        url=None,
        enabled_javascript=False,
        commands=[MockCommand()],
        callback=Callback(
            body=[],
            headers=[],
            method="POST",
            retries=1,
            timeout="1s",
            url=""
        ),
        storage_config=StorageConfig(backend="memory")
    )

    thread = Thread(target=schedule_process, args=(config, mock_function))
    thread.start()
    thread.join()

    # Test passes if schedule_process completes without errors

from threading import Thread
from time import sleep
import pytest
from prometheus_client import REGISTRY

from app.prometheus_collector import CollectorManager
from app.config import Callback, Config, StorageConfig
from app.websitewebhook import schedule_process
from test.mock import MockCommand


# prepare test environment up to yield
# tear down test environment after yield
@pytest.fixture(autouse=True)
def setup_collectors():
    CollectorManager.register_collectors()
    yield
    # Clear the registry after all tests
    REGISTRY._collector_to_names.clear()
    REGISTRY._names_to_collectors.clear()
    CollectorManager._collectors.clear()


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

    last_execution = REGISTRY.get_sample_value(
        f'{CollectorManager.LAST_COMMAND_EXECUTION}')
    next_execution = REGISTRY.get_sample_value(
        f'{CollectorManager.NEXT_COMMAND_EXECUTION}')

    assert last_execution > 0
    assert next_execution > 0

import pytest
from prometheus_client import REGISTRY

from app.command.prometheus_collector import CollectorManager, ExecutionStatus


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


def test_register_collectors():
    assert CollectorManager.CALLBACK_EXECUTION in CollectorManager._collectors
    assert CollectorManager.COMMAND_EXECUTION in CollectorManager._collectors


def test_inc_callback_execution_failure():
    initial_value = REGISTRY.get_sample_value(
        f'{CollectorManager.CALLBACK_EXECUTION}_total',
        {'status': ExecutionStatus.FAILURE.value}
    ) or 0
    CollectorManager.inc_callback_execution(ExecutionStatus.FAILURE)
    new_value = REGISTRY.get_sample_value(
        f'{CollectorManager.CALLBACK_EXECUTION}_total',
        {'status': ExecutionStatus.FAILURE.value}
    )
    assert new_value == initial_value + 1


def test_inc_command_execution_failure():
    initial_value = REGISTRY.get_sample_value(
        f'{CollectorManager.COMMAND_EXECUTION}_total',
        {'status': ExecutionStatus.FAILURE.value}
    ) or 0
    CollectorManager.inc_command_execution(ExecutionStatus.FAILURE)
    new_value = REGISTRY.get_sample_value(
        f'{CollectorManager.COMMAND_EXECUTION}_total',
        {'status': ExecutionStatus.FAILURE.value}
    )
    assert new_value == initial_value + 1


def test_inc_command_execution_success():
    initial_value = REGISTRY.get_sample_value(
        f'{CollectorManager.COMMAND_EXECUTION}_total',
        {'status': ExecutionStatus.SUCCESS.value}
    ) or 0
    CollectorManager.inc_command_execution(ExecutionStatus.SUCCESS)
    new_value = REGISTRY.get_sample_value(
        f'{CollectorManager.COMMAND_EXECUTION}_total',
        {'status': ExecutionStatus.SUCCESS.value}
    )
    assert new_value == initial_value + 1


def test_multiple_increments():
    initial_value = REGISTRY.get_sample_value(
        f'{CollectorManager.CALLBACK_EXECUTION}_total',
        {'status': ExecutionStatus.SUCCESS.value}
    ) or 0
    for _ in range(3):
        CollectorManager.inc_callback_execution(
            ExecutionStatus.SUCCESS)
    new_value = REGISTRY.get_sample_value(
        f'{CollectorManager.CALLBACK_EXECUTION}_total',
        {'status': ExecutionStatus.SUCCESS.value}
    )
    assert new_value == initial_value + 3


def test_different_statuses():
    CollectorManager.inc_callback_execution(ExecutionStatus.SUCCESS)
    CollectorManager.inc_callback_execution(ExecutionStatus.FAILURE)
    assert REGISTRY.get_sample_value(f'{CollectorManager.CALLBACK_EXECUTION}_total', {
                                     'status': ExecutionStatus.SUCCESS.value}) == 1
    assert REGISTRY.get_sample_value(f'{CollectorManager.CALLBACK_EXECUTION}_total', {
                                     'status': ExecutionStatus.FAILURE.value}) == 1

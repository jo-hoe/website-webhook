import ast
from prometheus_client import REGISTRY
import pytest
import responses

from app.command.prometheus_collector import CollectorManager, ExecutionStatus
from app.config import Callback, NameValuePair
from app.command.commandinvoker import CommandInvoker
from test.mock import MockCommand, MockScraper


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


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_execute_all_commands():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'status': 200
    })

    command = MockCommand("test-name", "test-url",
                          MockScraper(["a", "b"]), return_values=[False, True])
    callback = Callback(
        url=callback_test_url,
        method=callback_test_method,
        retries=0,
        timeout="12s",
        headers=[],
        body=[]
    )
    invoker = CommandInvoker([command], callback)

    invoker.execute_all_commands()
    invoker.execute_all_commands()

    assert REGISTRY.get_sample_value(f'{CollectorManager.CALLBACK_EXECUTION}_total', {
                                     'status': ExecutionStatus.SUCCESS.value}) == 1
    assert REGISTRY.get_sample_value(f'{CollectorManager.CALLBACK_EXECUTION}_total', {
                                     'status': ExecutionStatus.FAILURE.value}) == None
    assert REGISTRY.get_sample_value(f'{CollectorManager.COMMAND_EXECUTION}_total', {
                                     'status': ExecutionStatus.SUCCESS.value}) == 2


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_retries():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    response = responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'status': 500
    })

    command = MockCommand("test-name", "test-url",
                          MockScraper(["a", "b"]), return_values=[True])
    callback = Callback(
        url=callback_test_url,
        method=callback_test_method,
        retries=2,
        timeout="12s",
        headers=[],
        body=[]
    )
    invoker = CommandInvoker([command], callback)

    invoker.execute_all_commands()

    assert response.call_count == callback.retries + 1, "unexpected number of calls"
    assert REGISTRY.get_sample_value(f'{CollectorManager.COMMAND_EXECUTION}_total', {
                                     'status': ExecutionStatus.SUCCESS.value}) == 1


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_replace_placeholder():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    response = responses.add(**{
        'url': callback_test_url,
        'method': callback_test_method,
        'status': 200
    })

    command = MockCommand("test-name", "test-url",
                          MockScraper([""]), return_values=[True])
    callback = Callback(
        url=callback_test_url,
        method=callback_test_method,
        retries=2,
        timeout="12s",
        headers=[
                NameValuePair("header1", "<<url>>"),
                NameValuePair("header2", "<<commands.test-name.name>>")
        ],
        body=[
            NameValuePair("body1", "<<url>>"),
            NameValuePair("body2", "<<commands.test-name.name>>")
        ]
    )
    invoker = CommandInvoker([command], callback)

    invoker.execute_all_commands()

    assert response.call_count == 1, "unexpected number of calls"
    assert response.calls[0].request.headers["header1"] == "test-url", "unexpected header"
    assert response.calls[0].request.headers["header2"] == "test-name", "unexpected header"
    body = ast.literal_eval(response.calls[0].request.body)
    assert body["body1"] == "test-url", "unexpected body"
    assert body["body2"] == "test-name", "unexpected body"


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_failing_commands():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    response = responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'body': '{}',
        'status': 200,
        'content_type': 'application/json'
    })

    exception_command = MockCommand("failing-command", "test-url",
                                    MockScraper([""]), return_values=[False], raise_exception=True)
    successful_command = MockCommand("successful-command", "test-url",
                                     MockScraper([""]), return_values=[False], raise_exception=False)
    callback = Callback(
        url=callback_test_url,
        method=callback_test_method,
        retries=2,
        timeout="12s",
        headers=[],
        body=[]
    )
    invoker = CommandInvoker([successful_command, exception_command, successful_command], callback)

    invoker.execute_all_commands()

    assert response.call_count == 0, "unexpected number of calls"
    assert REGISTRY.get_sample_value(f'{CollectorManager.COMMAND_EXECUTION}_total', {
                                     'status': ExecutionStatus.FAILURE.value}) == 1
    assert REGISTRY.get_sample_value(f'{CollectorManager.COMMAND_EXECUTION}_total', {
                                     'status': ExecutionStatus.SUCCESS.value}) == 1

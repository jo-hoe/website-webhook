import ast
from typing import Mapping
import pytest
import responses

from app.config import Callback, NameValuePair
from app.command.commandinvoker import CommandInvoker
from test.mock import MockCommand, MockScraper


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_execute_all_commands():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'body': '{}',
        'status': 200,
        'content_type': 'application/json',
        'adding_headers': {'X-Foo': 'Bar'}
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

    assert invoker.execute_all_commands(
    ) == None, "execute_all_commands return unexpected value"
    assert invoker.execute_all_commands() == 200, "call unsuccessful"


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_retries():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    response = responses.add(**{
        'method': callback_test_method,
        'url': callback_test_url,
        'body': '{}',
        'status': 500,
        'content_type': 'application/json',
        'adding_headers': {'X-Foo': 'Bar'}
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

    assert invoker.execute_all_commands() == 500, "call unsuccessful"
    assert response.call_count == callback.retries + 1, "unexpected number of calls"


@pytest.mark.integration_test
@responses.activate
def test_commandinvoker_replace_placeholder():
    callback_test_url = "http://example.com/api/123"
    callback_test_method = responses.POST

    # callback mocking
    response = responses.add(**{
        'url': callback_test_url,
        'method': callback_test_method,
        'body': '{}',
        'status': 200,
        'content_type': 'application/json',
        'adding_headers': {'X-Foo': 'Bar'}
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

    assert invoker.execute_all_commands() == 200, "call unsuccessful"
    assert response.call_count == 1, "unexpected number of calls"
    
    assert response.calls[0].request.headers["header1"] == "test-url", "unexpected header"
    assert response.calls[0].request.headers["header2"] == "test-name", "unexpected header"

    body = ast.literal_eval(response.calls[0].request.body)
    assert body["body1"] == "test-url", "unexpected body"
    assert body["body2"] == "test-name", "unexpected body"

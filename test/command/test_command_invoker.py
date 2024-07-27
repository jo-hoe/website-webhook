import pytest
import responses

from app.config import Callback
from app.command.commandinvoker import CommandInvoker
from test.mock import MockCommand, MockScraper


@pytest.mark.integration_test
@responses.activate
def test_command_invoker():
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

    command = MockCommand("mock", "test-name", "test-url",
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

import pytest
import responses

from app.command.callback_handler import HttpCallbackHandler, LoggingCallbackHandler
from app.config import Callback


def _make_callback(url: str, retries: int = 0) -> Callback:
    return Callback(url=url, method="POST", timeout="5s", retries=retries, headers=[], body=[])


def _make_prepared_request(url: str):
    import json
    import requests
    return requests.Request(
        method="POST",
        url=url,
        headers={"Content-Type": "application/json"},
        data=json.dumps({"key": "value"}),
    ).prepare()


class TestLoggingCallbackHandler:
    def test_returns_true_without_sending(self):
        handler = LoggingCallbackHandler()
        request = _make_prepared_request("http://example.com/callback")
        callback = _make_callback("http://example.com/callback")

        result = handler.handle(request, callback)

        assert result is True

    def test_does_not_make_http_call(self):
        handler = LoggingCallbackHandler()
        request = _make_prepared_request("http://example.com/callback")
        callback = _make_callback("http://example.com/callback")

        # No responses mock active — any real HTTP call would raise a ConnectionError
        result = handler.handle(request, callback)

        assert result is True


class TestHttpCallbackHandler:
    @responses.activate
    def test_returns_true_on_success(self):
        url = "http://example.com/callback"
        responses.add(method=responses.POST, url=url, status=200)

        handler = HttpCallbackHandler()
        result = handler.handle(_make_prepared_request(url), _make_callback(url))

        assert result is True
        assert len(responses.calls) == 1

    @responses.activate
    def test_returns_false_on_server_error(self):
        url = "http://example.com/callback"
        responses.add(method=responses.POST, url=url, status=500)

        handler = HttpCallbackHandler()
        result = handler.handle(_make_prepared_request(url), _make_callback(url, retries=0))

        assert result is False

    @responses.activate
    def test_retries_on_failure(self):
        url = "http://example.com/callback"
        responses.add(method=responses.POST, url=url, status=500)

        retries = 2
        handler = HttpCallbackHandler()
        handler.handle(_make_prepared_request(url), _make_callback(url, retries=retries))

        assert len(responses.calls) == retries + 1

    @responses.activate
    def test_stops_retrying_on_success(self):
        url = "http://example.com/callback"
        responses.add(method=responses.POST, url=url, status=500)
        responses.add(method=responses.POST, url=url, status=200)

        handler = HttpCallbackHandler()
        result = handler.handle(_make_prepared_request(url), _make_callback(url, retries=5))

        assert result is True
        assert len(responses.calls) == 2

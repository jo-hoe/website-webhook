import json
import logging
from abc import ABC, abstractmethod
from typing import Optional

import requests

from app.config import Callback


class CallbackHandler(ABC):
    @abstractmethod
    def handle(self, request: requests.PreparedRequest, callback: Callback) -> bool:
        """Execute or simulate the prepared request. Returns True on success."""


class LoggingCallbackHandler(CallbackHandler):
    def handle(self, request: requests.PreparedRequest, callback: Callback) -> bool:
        _log_request(request)
        return True


class HttpCallbackHandler(CallbackHandler):
    def handle(self, request: requests.PreparedRequest, callback: Callback) -> bool:
        _log_request(request)
        response: Optional[requests.Response] = None
        with requests.Session() as session:
            retry_count = 0
            while True:
                try:
                    response = session.send(request, timeout=callback.timeout.seconds)
                except Exception as ex:
                    logging.error(f"Request send failed: {ex}")
                    response = None
                retry_count += 1
                if (response is not None and response.ok) or retry_count > callback.retries:
                    break
        if response is not None and not response.ok:
            logging.error(f"Request failed {response.status_code}: {response.reason}")
        return response is not None and response.ok


def _log_request(request: requests.PreparedRequest) -> None:
    try:
        body = json.dumps(json.loads(request.body), indent=2)
    except Exception:
        body = request.body or ""
    headers = "\n".join(f"  {k}: {v}" for k, v in request.headers.items())
    logging.info(
        "\n=== Outgoing REST Request ===\n"
        f"{request.method} {request.url}\n\n"
        f"Headers:\n{headers}\n\n"
        f"Body:\n{body}\n"
        "============================="
    )

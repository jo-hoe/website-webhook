import json
import logging
import requests

from typing import List
from app.command.command import Command
from app.config import Callback, NameValuePair


class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback):
        self.commands = commands
        self.callback = callback
        self.cached_request = None

    def execute_all_commands(self) -> int:
        """
        returns response code of callback, if no callback is required returns None 
        """
        triggerCallback = False

        request = None
        for command in self.commands:
            triggerCallback = command.execute()

        if triggerCallback:
            request = self._build_request()

        if not triggerCallback and self.cached_request is not None:
            logging.info("Using cached request")
            request = self.cached_request

        if request is not None:
            logging.info("Sending callback")
            response_code = self._send_callback(request)

            if response_code <= 400:
                logging.info("Callback sent successfully")
                self.cached_request = None
            else:
                logging.error(
                    f"Callback send failed, caching request")
                self.cached_request = request

            return response_code
        else:
            logging.info("No callback required")

        return None

    def _template(self, input: List[NameValuePair], command: Command) -> List[NameValuePair]:
        result = []

        for element in input:
            templatedElement = NameValuePair(
                name=element.name,
                value=command.replace_placeholder(element.value)
            )
            result.append(templatedElement)

        return result

    def _build_request(self):
        templatedHeaders = []
        templatedBody = []

        for command in self.commands:
            templatedHeaders = self._template(self.callback.headers, command)
            templatedBody = self._template(self.callback.body, command)

        data = {
            body.name: body.value
            for body in templatedBody
        }

        request = requests.Request(
            method=self.callback.method.upper(),
            url=self.callback.url,
            headers={
                header.name: header.value
                for header in templatedHeaders
            },
            data=json.dumps(data))

        return request.prepare()

    def _send_callback(self, request) -> int:
        session = requests.Session()

        stop = False
        retry_count = 0

        while not stop:
            response = session.send(
                request, timeout=self.callback.timeout.seconds)
            retry_count += 1
            stop = response.ok or retry_count >= self.callback.retries

        if response.ok:
            logging.info("Request send successfully")
        else:
            logging.error(
                f"Request send failed for this amount of calls:{retry_count} last response: {response.status_code}: {response.text}")

        return response.status_code

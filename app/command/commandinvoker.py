import json
import logging
import requests

from typing import List
from app.command.command import Command
from app.command.prometheus_collector import CollectorManager, ExecutionStatus
from app.config import Callback, NameValuePair


class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback):
        self.commands = commands
        self.callback = callback
        self.cached_request = None

    def execute_all_commands(self) -> None:
        triggerCallback = False

        request = None
        for command in self.commands:
            try:
                triggerCallback = command.execute()
                CollectorManager.inc_command_execution(
                    ExecutionStatus.SUCCESS)
            except Exception as ex:
                CollectorManager.inc_command_execution(
                    ExecutionStatus.FAILURE)
                logging.error(
                    f"Command '{command.name}' failed due to exception '{ex}'. Cancelling execution.")
                return

        if triggerCallback:
            request = self._build_request()

        if not triggerCallback and self.cached_request is not None:
            logging.info("Using cached request")
            request = self.cached_request

        if request is not None:
            logging.info("Sending callback")
            success = self._send_callback(request)
            if success:
                CollectorManager.inc_callback_execution(
                    ExecutionStatus.SUCCESS)
            else:
                CollectorManager.inc_callback_execution(
                    ExecutionStatus.FAILURE)

            if success:
                logging.info("Callback sent successfully")
                self.cached_request = None
            else:
                logging.error(
                    f"Callback send failed, caching request")
                self.cached_request = request

            return success
        else:
            logging.info("No callback required")

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
        templatedHeaders = self.callback.headers
        templatedBody = self.callback.body

        for command in self.commands:
            templatedHeaders = self._template(templatedHeaders, command)
            templatedBody = self._template(templatedBody, command)

        data = {
            body.name: body.value
            for body in templatedBody
        }
        headers = {
            header.name: header.value
            for header in templatedHeaders
        }

        request = requests.Request(
            method=self.callback.method.upper(),
            url=self.callback.url,
            headers=headers,
            data=json.dumps(data))

        return request.prepare()

    def _send_callback(self, request: requests.PreparedRequest) -> bool:
        success = False
        session = requests.Session()

        retry_count = 0
        stop = False
        while not stop:
            response = None
            try:
                response = session.send(
                    request, timeout=self.callback.timeout.seconds)
            except BaseException as ex:
                logging.error(f"Request send failed: {ex}")
            retry_count += 1
            stop = (response and response.ok) or retry_count > self.callback.retries

        if response is not None:
            if not response.ok:
                logging.error(
                    f"Request send failed {response.status_code}: {response.reason}")
            success = response.ok

        return success

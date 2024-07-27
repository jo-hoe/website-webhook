import logging
import requests

from typing import List
from app.command.command import Command
from app.config import Callback, NameValuePair


class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback):
        self.commands = commands
        self.callback = callback

    def executeAllCommands(self):
        triggerCallback = False

        for command in self.commands:
            triggerCallback = command.execute()

        if triggerCallback:
            self._send_callback()

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

        request = requests.Request(
            method=self.callback.method.upper(),
            url=self.callback.url,
            headers={
                header.name: header.value
                for header in templatedHeaders
            },
            data={
                body.name: body.value
                for body in templatedBody
            })

        return request.prepare()

    def _send_callback(self):
        request = self._build_request()
        session = requests.Session()
        response = session.send(request, timeout=self.callback.timeout,
                                retries=self.callback.retries)

        if response.ok:
            logging.info("request send successfully")
        else:
            logging.error(f"request send failed {
                          response.status_code}: {response.text}")

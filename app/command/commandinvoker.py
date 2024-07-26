import logging
import requests

from typing import List
from app.command.command import Command
from app.config.config import Callback, NameValuePair


class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback):
        self.commands = commands
        self.callback = callback

    def executeAllCommands(self):
        for command in self.commands:
            triggerCallback = command.execute()
            if triggerCallback:
                self.sendCallback()

    def template(self, input: List[NameValuePair], command: Command) -> List[NameValuePair]:
        result = []

        for element in input:
            templatedElement = NameValuePair(
                name=element.name,
                value=command.template(element.value)
            )
            result.append(templatedElement)

        return result

    def sendCallback(self):
        templatedHeaders = []
        templatedBody = []

        for command in self.commands:
            templatedHeaders = self.template(self.callback.headers, command)
            templatedBody = self.template(self.callback.body, command)

        response = requests.post(
            url=self.callback.url,
            headers={
                header.name: header.value
                for header in templatedHeaders
            },
            data={
                body.name: body.value
                for body in templatedBody
            }
        )

        if response.status_code >= 200 and response.status_code <= 300:
            logging.info("request send successfully")
        else:
            logging.error(f"request send failed {
                          response.status_code}: {response.text}")

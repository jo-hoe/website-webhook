import json
import logging

from typing import List

import requests

from app.command.callback_handler import CallbackHandler
from app.command.command import Command
from app.command.stateful_command import StatefulCommand
from app.config import Callback, NameValuePair


class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback, handler: CallbackHandler) -> None:
        self.commands = commands
        self.callback = callback
        self.handler = handler
        self.cached_request = None

    def execute_all_commands(self) -> None:
        """
        Execute all commands with a strict execute/commit lifecycle.
        - Always call command.execute() first (no persistence).
        - If any command requests a callback, build and handle it.
        - Commit state only after a successful callback, or immediately if no callback is required.
        """
        trigger_any = False

        for command in self.commands:
            try:
                result = command.execute()
                trigger_any = result or trigger_any
            except Exception as ex:
                logging.error(
                    f"Command '{command.name}' failed due to exception '{ex}'. Cancelling execution.")
                raise

        request = None
        if trigger_any:
            request = self._build_request()
        elif self.cached_request is not None:
            logging.info("Using cached request")
            request = self.cached_request

        if request is not None:
            logging.info("Sending callback")
            success = self.handler.handle(request, self.callback)

            if success:
                logging.info("Callback sent successfully")
                self.cached_request = None
                for cmd in self.commands:
                    if isinstance(cmd, StatefulCommand):
                        cmd.commit_state()
            else:
                logging.error("Callback send failed, caching request")
                self.cached_request = request
                raise RuntimeError("Callback send failed")
        else:
            for cmd in self.commands:
                if isinstance(cmd, StatefulCommand):
                    cmd.commit_state()
            logging.info("No callback required")

    def _build_request(self):
        templated_headers = self.callback.headers
        templated_body = self.callback.body

        for command in self.commands:
            templated_headers = self._template(templated_headers, command)
            templated_body = self._template(templated_body, command)

        data = {body.name: body.value for body in templated_body}
        headers = {header.name: header.value for header in templated_headers}

        return requests.Request(
            method=self.callback.method.upper(),
            url=self.callback.url,
            headers=headers,
            data=json.dumps(data),
        ).prepare()

    def _template(self, input: List[NameValuePair], command: Command) -> List[NameValuePair]:
        return [
            NameValuePair(name=element.name, value=command.replace_placeholder(element.value))
            for element in input
        ]

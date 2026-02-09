import json
import logging
import requests

from typing import List
from app.command.command import Command
from app.config import Callback, NameValuePair


from app.command.stateful_command import StatefulCommand

class CommandInvoker:

    def __init__(self, commands: List[Command], callback: Callback):
        self.commands = commands
        self.callback = callback
        self.cached_request = None

    def execute_all_commands(self) -> None:
        """
        Execute all commands with a strict execute/commit lifecycle.
        - Always call command.execute() first (no persistence).
        - If any command requests a callback, send it.
        - Commit state only after a successful callback send, or immediately if no callback is required.
        """
        trigger_any = False
        request = None

        # execute (no commit yet)
        for command in self.commands:
            try:
                result = command.execute()
                trigger_any = result or trigger_any
            except Exception as ex:
                logging.error(
                    f"Command '{command.name}' failed due to exception '{ex}'. Cancelling execution.")
                raise  # Re-raise the exception to signal failure

        # build request if any change detected (or use cached)
        if trigger_any:
            request = self._build_request()

        if not trigger_any and self.cached_request is not None:
            logging.info("Using cached request")
            request = self.cached_request

        # send (and commit on success)
        if request is not None:
            logging.info("Sending callback")
            success = self._send_callback(request)

            if success:
                logging.info("Callback sent successfully")
                self.cached_request = None
                # Commit state for stateful commands only
                for cmd in self.commands:
                    if isinstance(cmd, StatefulCommand):
                        cmd.commit_state()
            else:
                logging.error("Callback send failed, caching request")
                self.cached_request = request
                # Do NOT commit here; commit-after-success ensures retry in job mode
                raise RuntimeError("Callback send failed")
        else:
            # No callback needed; commit baseline/pending state immediately for stateful commands
            for cmd in self.commands:
                if isinstance(cmd, StatefulCommand):
                    cmd.commit_state()
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
        response = None
        
        with requests.Session() as session:
            retry_count = 0
            stop = False
            while not stop:
                try:
                    response = session.send(
                        request, timeout=self.callback.timeout.seconds)
                except BaseException as ex:
                    logging.error(f"Request send failed: {ex}")
                    response = None
                retry_count += 1
                stop = (response and response.ok) or retry_count > self.callback.retries

        if response is not None:
            if not response.ok:
                logging.error(
                    f"Request send failed {response.status_code}: {response.reason}")
            success = response.ok

        return success

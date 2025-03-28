
import logging
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, Command, CommandException
from app.scraper.scraper import Scraper
from app.templating import template


class TriggerCallbackOnChangedState(Command):

    KIND = "triggerCallbackOnChangedState"

    def __init__(self, name: str, url: str, xpath: str, scraper: Scraper) -> None:
        super().__init__(self.KIND, name, url, scraper)
        self._xpath = xpath
        self._old_value = None
        self._new_value = None

    def execute(self) -> bool:
        trigger_callback = False
        logging.info(f"Last seen value: '{self._old_value}'")
        current_value = self._scraper.scrape(self._url, self._xpath)
        logging.info(f"Current value: '{current_value}'")

        if current_value == None:
            logging.error(f"Could not read value for xpath '{self._xpath}'")
            raise CommandException(
                f"Could not read value for xpath '{self._xpath}'")

        if self._old_value == None:
            self._old_value = current_value
        if self._new_value == None:
            self._new_value = current_value

        if self._new_value != current_value:
            logging.info(
                f"Triggering callback'")
            trigger_callback = True

        self._old_value = self._new_value
        self._new_value = current_value

        return trigger_callback

    def replace_placeholder(self, input: str) -> str:
        result = super().replace_placeholder(input)

        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.old", result, self._old_value)
        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.new", result, self._new_value)

        return result

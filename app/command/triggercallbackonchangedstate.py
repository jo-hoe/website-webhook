
import logging
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, Command, CommandException
from app.scraper.scraper import Scraper
from app.templating import template


class TriggerCallbackOnChangedState(Command):

    KIND = "triggerCallbackOnChangedState"

    def __init__(self, name: str, url: str, xpath: str, scraper: Scraper, exception_on_not_found: bool = True) -> None:
        super().__init__(self.KIND, name, url, scraper)
        self._xpath = xpath
        self._exception_on_not_found = exception_on_not_found
        self._old_value = None
        self._new_value = None

    def execute(self) -> bool:
        trigger_callback = False
        logging.info(f"Last seen value: '{self._old_value}'")

        try:
            current_value = self._scraper.scrape(self._url, self._xpath)
        except Exception as ex:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}': {ex}")
            else:
                logging.warning(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                if self._old_value == None:
                    self._old_value = ""
                return trigger_callback

        logging.info(f"Current value: '{current_value}'")

        if current_value == None:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Found 'None' value for xpath '{self._xpath}'")
            else:
                logging.warning(
                    f"Found 'None' value for xpath '{self._xpath}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                if self._old_value == None:
                    self._old_value = ""
                return trigger_callback

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

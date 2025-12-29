
import logging
from typing import Optional
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, CommandException
from app.command.stateful_command import StatefulCommand
from app.scraper.scraper import Scraper
from app.storage.state_storage import StateStorage
from app.templating import template


class TriggerCallbackOnChangedState(StatefulCommand):

    KIND = "triggerCallbackOnChangedState"
    STATE_KEY_PREVIOUS = "previous"
    STATE_KEY_CURRENT = "current"

    def __init__(self, name: str, url: str, xpath: str, scraper: Scraper, 
                 storage: Optional[StateStorage] = None, exception_on_not_found: bool = True) -> None:
        super().__init__(self.KIND, name, url, scraper, storage)
        self._xpath = xpath
        self._exception_on_not_found = exception_on_not_found

    def execute(self) -> bool:
        trigger_callback = False
        
        # Retrieve stored values
        previous_value = self._get_state(self.STATE_KEY_PREVIOUS)
        current_stored_value = self._get_state(self.STATE_KEY_CURRENT)
        
        logging.info(f"Last seen value: '{previous_value}'")

        try:
            scraped_value = self._scraper.scrape(self._url, self._xpath)
        except Exception as ex:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}': {ex}")
            else:
                logging.warning(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                if previous_value is None:
                    self._set_state(self.STATE_KEY_PREVIOUS, "")
                return trigger_callback

        logging.info(f"Current value: '{scraped_value}'")

        if scraped_value is None:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Found 'None' value for xpath '{self._xpath}'")
            else:
                logging.warning(
                    f"Found 'None' value for xpath '{self._xpath}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                if previous_value is None:
                    self._set_state(self.STATE_KEY_PREVIOUS, "")
                return trigger_callback

        # Initialize values on first run
        if previous_value is None:
            self._set_state(self.STATE_KEY_PREVIOUS, scraped_value)
        if current_stored_value is None:
            self._set_state(self.STATE_KEY_CURRENT, scraped_value)
            current_stored_value = scraped_value

        # Check if value has changed
        if current_stored_value != scraped_value:
            logging.info(
                f"Triggering callback'")
            trigger_callback = True
        elif previous_value == "" and scraped_value != "":
            # Special case: transitioning from error state (no value found) to first real value
            logging.info(
                f"Triggering callback'")
            trigger_callback = True

        # Update stored values: previous ← current, current ← scraped
        self._set_state(self.STATE_KEY_PREVIOUS, current_stored_value)
        self._set_state(self.STATE_KEY_CURRENT, scraped_value)

        return trigger_callback

    def replace_placeholder(self, input: str) -> str:
        result = super().replace_placeholder(input)

        previous_value = self._get_state(self.STATE_KEY_PREVIOUS) or ""
        current_value = self._get_state(self.STATE_KEY_CURRENT) or ""

        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.old", result, previous_value)
        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.new", result, current_value)

        return result

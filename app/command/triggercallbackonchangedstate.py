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

        # Pending values used for commit-after-success flow
        self._pending_previous_value: Optional[str] = None
        self._pending_current_value: Optional[str] = None

    def execute(self) -> bool:
        """
        Detect whether a change occurred and prepare pending state values,
        but DO NOT commit to storage yet. Returns True if a callback should be triggered.
        """
        trigger_callback = False

        # Retrieve stored values
        previous_value = self._get_state(self.STATE_KEY_PREVIOUS)
        current_stored_value = self._get_state(self.STATE_KEY_CURRENT)

        logging.info(f"Stored previous value: '{previous_value}'")
        logging.info(f"Stored current value: '{current_stored_value}'")

        try:
            scraped_value = self._scraper.scrape(self._url, self._xpath)
        except Exception as ex:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}': {ex}")
            else:
                logging.warning(
                    f"Could not read value for xpath '{self._xpath}' in url '{self._url}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                # On first run when no previous exists, record error marker for previous
                if previous_value is None:
                    self._pending_previous_value = ""
                    self._pending_current_value = None
                return trigger_callback

        logging.info(f"Freshly scraped value: '{scraped_value}'")

        if scraped_value is None:
            if self._exception_on_not_found:
                raise CommandException(
                    f"Found 'None' value for xpath '{self._xpath}'")
            else:
                logging.warning(
                    f"Found 'None' value for xpath '{self._xpath}'. Skipping since exceptionOnNotFound is {self._exception_on_not_found}.")
                if previous_value is None:
                    self._pending_previous_value = ""
                    self._pending_current_value = None
                return trigger_callback

        # Determine effective current for comparison (handles first run)
        effective_current = current_stored_value if current_stored_value is not None else scraped_value

        # Prepare pending commit values to mirror original behavior:
        # previous <- current (or scraped on first run), current <- scraped
        pending_previous = scraped_value if previous_value is None else effective_current
        pending_current = scraped_value

        self._pending_previous_value = pending_previous
        self._pending_current_value = pending_current

        # Check if value has changed
        if effective_current != scraped_value:
            logging.info(
                f"Change detected (stored current -> scraped): '{effective_current}' -> '{scraped_value}'. Triggering callback")
            trigger_callback = True
        elif previous_value == "" and scraped_value != "":
            # Special case: transitioning from error state (no value found) to first real value
            logging.info("Recovered from previous error state (empty previous value). Triggering callback")
            trigger_callback = True

        # Do not commit here; let the invoker decide when to commit.
        return trigger_callback

    def commit_state(self) -> None:
        """
        Commit the prepared pending values to storage. This should be called
        only after a successful callback send, or immediately if no callback is required.
        """
        # Nothing to commit
        if self._pending_previous_value is None and self._pending_current_value is None:
            return

        # Update stored values: previous ← pending_previous, current ← pending_current
        logging.info(
            f"Committing state: previous <- '{self._pending_previous_value}', current <- '{self._pending_current_value}'")

        if self._pending_previous_value is not None:
            self._set_state(self.STATE_KEY_PREVIOUS, self._pending_previous_value)
        if self._pending_current_value is not None:
            self._set_state(self.STATE_KEY_CURRENT, self._pending_current_value)

        # Clear pending values
        self._pending_previous_value = None
        self._pending_current_value = None


    def replace_placeholder(self, input: str) -> str:
        result = super().replace_placeholder(input)

        # Use pending values if present (pre-commit) to allow correct templating for callbacks
        if self._pending_previous_value is not None and self._pending_current_value is not None:
            previous_value = self._pending_previous_value or ""
            current_value = self._pending_current_value or ""
        else:
            previous_value = self._get_state(self.STATE_KEY_PREVIOUS) or ""
            current_value = self._get_state(self.STATE_KEY_CURRENT) or ""

        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.old", result, previous_value)
        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.new", result, current_value)

        return result
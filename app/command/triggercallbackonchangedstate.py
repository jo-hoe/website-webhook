
from app import scraper
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, Command
from app.templating import template

KIND = "TriggerCallbackOnChangedState"


class TriggerCallbackOnChangedState(Command):

    def __init__(self, name: str, url: str, xpath: str) -> None:
        super().__init__(KIND, name, url)
        self._xpath = xpath
        self._old_value = None
        self._new_value = None

    def execute(self) -> bool:
        trigger_callback = False
        current_value = scraper.scrape(self._url, self._xpath)

        if self._old_value == None:
            self._old_value = current_value
        if self._new_value == None:
            self._new_value = current_value

        if self._new_value != current_value:
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

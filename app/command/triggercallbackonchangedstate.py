
from app import scraper
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, Command
from app.templating import PLACEHOLDER_END, PLACEHOLDER_START, template


class TriggerCallbackOnChangedState(Command):

    def __init__(self, kind: str, name: str, xpath: str) -> None:
        super().__init__(kind, name)
        self.xpath = xpath
        self.old_value = None

    def execute(self, url: str) -> bool:
        new_value = scraper(url, self.xpath)

        if self.old_value == None:
            # first call
            self.old_value = new_value
            return False
        elif new_value == self.old_value:
            # no change detected
            return False

        # change detected
        self.old_value = new_value
        return True

    def replace_placeholder(self, input: str) -> str:
        result = super().replace_placeholder(input)

        result = template(f"{PLACEHOLDER_START}{PLACEHOLDER_COMMANDS_PREFIX}.{self.name}{PLACEHOLDER_END}.old", result, self.old_value)
        result = template(f"{PLACEHOLDER_START}{PLACEHOLDER_COMMANDS_PREFIX}.{self.name}{PLACEHOLDER_END}.new", result, self.new_value)

        return result

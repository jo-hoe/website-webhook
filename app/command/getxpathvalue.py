
import logging
from app import scraper
from app.command.command import PLACEHOLDER_COMMANDS_PREFIX, Command, CommandException
from app.templating import template


class GetXPathValue(Command):

    KIND = "getXPathValue"

    def __init__(self, name: str, url: str, xpath: str, scraper: scraper.Scraper) -> None:
        super().__init__(self.KIND, name, url, scraper)
        self._xpath = xpath
        self._value = None


    def execute(self) -> bool:
        self._value = self._scraper.scrape(self._url, self._xpath)
        logging.info(f"Retrieved value: '{self._value}'")

        if self._value == None:
            logging.error(f"Could not read value for xpath '{self._xpath}'")
            raise CommandException(
                f"Could not read value for xpath '{self._xpath}'")

        return False

    def replace_placeholder(self, input: str) -> str:
        result = super().replace_placeholder(input)

        result = template(
            f"{PLACEHOLDER_COMMANDS_PREFIX}{self._name}.value", result, self._value)
        
        return result

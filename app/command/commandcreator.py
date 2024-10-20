

from app.command.command import Command
from app.command.getxpathvalue import GetXPathValue
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from app.scraper.scraper_factory import ScraperFactory


def create_command(data: dict, url: str, enabled_javascript: bool) -> Command:
    kind = data["kind"]
    name = data["name"]

    if TriggerCallbackOnChangedState.KIND.lower() == kind.lower():
        return TriggerCallbackOnChangedState(name, url, data["xpath"], ScraperFactory.get_scraper(enabled_javascript))
    if GetXPathValue.KIND.lower() == kind.lower():
        return GetXPathValue(name, url, data["xpath"], ScraperFactory.get_scraper(enabled_javascript))
    else:
        raise NotImplementedError()

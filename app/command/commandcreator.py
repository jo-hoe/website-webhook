

from app.command.command import Command
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from app.scraper import Scraper


def create_command(data: dict, url) -> Command:
    kind = data["kind"]
    name = data["name"]

    if TriggerCallbackOnChangedState.KIND.lower() == kind.lower():
        return TriggerCallbackOnChangedState(TriggerCallbackOnChangedState.KIND, name, url, data["xpath"], Scraper())
    else:
        raise NotImplementedError()

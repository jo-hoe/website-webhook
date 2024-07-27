from datetime import timedelta
from typing import List

from app.command.commandcreator import create_command
from app.duration import parse_duration
from app.command.command import Command


class NameValuePair:
    name: str
    value: str

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value


class Callback:
    url: str
    method: str
    timeout: timedelta
    retries: int
    headers: List[NameValuePair]
    body: List[NameValuePair]

    def __init__(self, url: str, method: str, timeout: str, retries: int, headers: List[NameValuePair], body: List[NameValuePair]) -> None:
        self.url = url
        self.method = method
        self.retries = retries
        self.headers = headers
        self.body = body
        self.timeout = parse_duration(timeout)


class Config:
    interval: timedelta
    url: str
    commands: List[Command]
    callback: Callback

    def __init__(self, interval: str, url: str, commands: List[Command], callback: Callback) -> None:
        self.interval = parse_duration(interval)
        self.url = url
        self.commands = commands
        self.callback = callback


def create_config(path_to_yaml: str) -> Config:
    import yaml

    with open(path_to_yaml, "r") as f:
        config = yaml.safe_load(f)

    interval = config.get("interval", "1h")
    url = config.get("url", None)
    commands = []
    for command in config.get("commands", []):
        commands.append(create_command(command, url))

    callback = Callback(
        url=config.get("callback", {}).get("url", None),
        method=config.get("callback", {}).get("method", "POST").upper(),
        timeout=config.get("callback", {}).get("timeout", "24s"),
        retries=config.get("callback", {}).get("retries", 0),
        headers=[NameValuePair(name=header.get("name", None), value=header.get("value", None)) for header in config.get("callback", {}).get("headers", [])],
        body=[NameValuePair(name=body.get("name", None), value=body.get("value", None)) for body in config.get("callback", {}).get("body", [])],
    )

    return Config(interval=interval, url=url, commands=commands, callback=callback)

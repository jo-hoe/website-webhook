from typing import List


class NameValuePair:
    name: str
    value: str

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value


class Callback:
    url: str
    method: str
    timeout: str
    retries: int
    headers: List[NameValuePair]
    body: List[NameValuePair]

    def __init__(self, url: str, method: str, timeout: str, retries: int, headers: List[NameValuePair], body: List[NameValuePair]) -> None:
        self.url = url
        self.method = method
        self.retries = retries
        self.headers = headers
        self.body = body


class CommandConfig:
    kind: str
    name: str
    xpath: str

    def __init__(self, kind: str, name: str, xpath: str) -> None:
        self.kind = kind
        self.name = name
        self.xpath = xpath


class Config:
    interval: str
    url: str
    commands: List[CommandConfig]
    callback: Callback

    def __init__(self, interval: str, url: str, commands: List[CommandConfig], callback: Callback) -> None:
        self.interval = interval
        self.url = url
        self.commands = commands
        self.callback = callback

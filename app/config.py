import yaml
import os

from datetime import timedelta
from typing import List, Optional

from app.command.commandcreator import create_command
from app.duration import parse_duration
from app.command.command import Command
from app.storage.storage_factory import create_storage
from app.storage.state_storage import StateStorage


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


class StorageConfig:
    backend: str
    redis_host: Optional[str]
    redis_port: Optional[int]
    redis_db: Optional[int]
    redis_password: Optional[str]
    redis_key_prefix: Optional[str]

    def __init__(self, backend: str = "memory", redis_host: Optional[str] = None,
                 redis_port: Optional[int] = None, redis_db: Optional[int] = None,
                 redis_password: Optional[str] = None, redis_key_prefix: Optional[str] = None) -> None:
        self.backend = backend
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.redis_key_prefix = redis_key_prefix


class Config:
    cron: str
    url: str
    enabled_javascript: bool
    execute_on_start: bool
    commands: List[Command]
    callback: Callback
    storage_config: StorageConfig
    storage: StateStorage

    def __init__(self, cron: str, execute_on_start: bool, url: str,
                 enabled_javascript: bool, commands: List[Command], callback: Callback,
                 storage_config: StorageConfig) -> None:
        self.cron = cron
        self.url = url
        self.enabled_javascript = enabled_javascript
        self.execute_on_start = execute_on_start
        self.commands = commands
        self.callback = callback
        self.storage_config = storage_config
        self.storage = create_storage(
            backend=storage_config.backend,
            redis_host=storage_config.redis_host,
            redis_port=storage_config.redis_port,
            redis_db=storage_config.redis_db,
            redis_password=storage_config.redis_password,
            redis_key_prefix=storage_config.redis_key_prefix
        )


def create_config(path_to_yaml: str) -> Config:
    with open(path_to_yaml, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    cron = config.get("cron", "0 * * * *")
    url = config.get("url", None)
    execute_on_start = config.get("executeOnStartUp", True)
    enabled_javascript = config.get("enableJavaScript", False)
    # First create storage (needed before creating commands)
    storage_section = config.get("storage", {})
    storage_config = StorageConfig(
        backend=os.getenv("STORAGE_BACKEND", storage_section.get("backend", "memory")),
        redis_host=os.getenv("REDIS_HOST", storage_section.get("redis", {}).get("host")),
        redis_port=int(os.getenv("REDIS_PORT", storage_section.get("redis", {}).get("port", 6379))),
        redis_db=int(os.getenv("REDIS_DB", storage_section.get("redis", {}).get("db", 0))),
        redis_password=os.getenv("REDIS_PASSWORD", storage_section.get("redis", {}).get("password")),
        redis_key_prefix=os.getenv("REDIS_KEY_PREFIX", storage_section.get("redis", {}).get("keyPrefix", "website-webhook"))
    )
    
    storage = create_storage(
        backend=storage_config.backend,
        redis_host=storage_config.redis_host,
        redis_port=storage_config.redis_port,
        redis_db=storage_config.redis_db,
        redis_password=storage_config.redis_password,
        redis_key_prefix=storage_config.redis_key_prefix
    )

    commands = []
    for command in config.get("commands", []):
        commands.append(create_command(command, url, enabled_javascript, storage))

    callback = Callback(
        url=config.get("callback", {}).get("url", None),
        method=config.get("callback", {}).get("method", "POST").upper(),
        timeout=config.get("callback", {}).get("timeout", "24s"),
        retries=config.get("callback", {}).get("retries", 0),
        headers=[NameValuePair(name=header.get("name", None), value=header.get(
            "value", None)) for header in config.get("callback", {}).get("headers", [])],
        body=[NameValuePair(name=body.get("name", None), value=body.get(
            "value", None)) for body in config.get("callback", {}).get("body", [])],
    )

    return Config(cron=cron, url=url, execute_on_start=execute_on_start,
                  enabled_javascript=enabled_javascript, commands=commands, callback=callback,
                  storage_config=storage_config)

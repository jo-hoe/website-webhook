
import logging
from time import sleep
from threading import Thread
from datetime import datetime
from typing import Callable
from croniter import croniter

from app.command.commandinvoker import CommandInvoker
from app.prometheus_collector import CollectorManager
from app.config import Config, create_config


def start(config_path: str):
    config = create_config(config_path)
    thread = Thread(target=schedule_process, args=(config, execute))
    thread.start()


def execute(invoker: CommandInvoker) -> bool:
    logging.info("Executing commands")
    invoker.execute_all_commands()
    return False


def schedule_process(config: Config, func: Callable):
    invoker = CommandInvoker(config.commands, config.callback)
    cron = croniter(config.cron, datetime.now())

    if config.execute_on_start:
        logging.info("Running commands on startup")
        CollectorManager.set_last_command_execution(datetime.now())
        func(invoker)

    logging.info("Scheduling process")
    while True:
        next_execution = cron.get_next(datetime)
        CollectorManager.set_next_command_execution(next_execution)

        seconds_to_wait = (next_execution - datetime.now()).total_seconds()
        logging.info(f"Waiting {seconds_to_wait}s for next execution")
        if seconds_to_wait > 0:
            sleep(seconds_to_wait)

        CollectorManager.set_last_command_execution(datetime.now())
        stop = func(invoker)
        if stop:
            break

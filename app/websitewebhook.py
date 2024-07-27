
import logging
import os
import sys

from app.command.commandinvoker import CommandInvoker
from app.config import Config, create_config
from threading import Thread
from time import sleep


def start(config_path: str):
    config = create_config(config_path)
    thread = Thread(target=schedule_process, args=(config, ))
    thread.start()


def schedule_process(config: Config):
    invoker = CommandInvoker(config.commands, config.callback)

    logging.info("Scheduling process")

    while True:
        execute(invoker)
        logging.info(f"Waiting {config.interval.seconds}s for next execution")
        sleep(config.interval.seconds)


def execute(invoker: CommandInvoker):
    logging.info("Executing commands")
    invoker.execute_all_commands()

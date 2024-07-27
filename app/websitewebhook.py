
import logging
import os

from app.command.commandinvoker import CommandInvoker
from app.config import Config, create_config
from threading import Thread
from time import sleep

DEFAULT_CONFIG_PATH = "/run/config/config.yaml"


def start():
    config_path = os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
    config = create_config(config_path)
    thread = Thread(target=schedule_process, args=(config, ))
    thread.start()


def schedule_process(config: Config):
    invoker = CommandInvoker(config.commands, config.callback)

    logging.info("Scheduling process")

    while True:
        logging.info("Executing commands")
        invoker.execute_all_commands()

        logging.info("Waiting for next execution")
        sleep(config.interval)

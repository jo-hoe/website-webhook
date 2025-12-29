
import logging
from time import sleep
from threading import Thread, Event
from datetime import datetime
from typing import Callable
from croniter import croniter

from app.command.commandinvoker import CommandInvoker
from app.config import Config, create_config

# Global shutdown event
_shutdown_event = Event()


def execute_once(config_path: str):
    """Execute commands once and exit. Used for job mode."""
    config = create_config(config_path)
    invoker = CommandInvoker(config.commands, config.callback)
    logging.info("Executing commands in job mode")
    invoker.execute_all_commands()
    logging.info("Commands executed successfully")


def start_with_schedule(config_path: str) -> Thread:
    config = create_config(config_path)
    thread = Thread(target=schedule_process, args=(config, execute))
    thread.daemon = True  # Allow process to exit even if thread is running
    thread.start()
    return thread


def shutdown():
    """Signal the background thread to stop gracefully."""
    _shutdown_event.set()


def execute(invoker: CommandInvoker) -> bool:
    logging.info("Executing commands")
    invoker.execute_all_commands()
    return False


def schedule_process(config: Config, func: Callable):
    invoker = CommandInvoker(config.commands, config.callback)
    cron = croniter(config.schedule, datetime.now())

    if config.execute_on_start:
        logging.info("Running commands on startup")
        func(invoker)

    logging.info("Scheduling process")
    while not _shutdown_event.is_set():
        next_execution = cron.get_next(datetime)

        seconds_to_wait = (next_execution - datetime.now()).total_seconds()
        logging.info(f"Waiting {seconds_to_wait}s for next execution")
        if seconds_to_wait > 0:
            # Use event.wait() instead of sleep() to allow interruption
            if _shutdown_event.wait(timeout=seconds_to_wait):
                logging.info("Shutdown requested, stopping scheduler")
                break

        if _shutdown_event.is_set():
            break

        stop = func(invoker)
        if stop:
            break

    logging.info("Scheduler stopped")

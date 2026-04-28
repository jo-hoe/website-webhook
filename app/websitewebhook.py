
import logging
from time import sleep
from threading import Thread, Event
from datetime import datetime
from typing import Callable, Optional

from croniter import croniter

from app.command.callback_handler import HttpCallbackHandler, LoggingCallbackHandler
from app.command.commandinvoker import CommandInvoker
from app.command.triggercallbackonchangedstate import TriggerCallbackOnChangedState
from app.config import Config, create_config

# Global shutdown event
_shutdown_event = Event()


def execute_once(config_path: str) -> None:
    """Execute commands once and exit. Used for job mode."""
    config = create_config(config_path)
    invoker = CommandInvoker(config.commands, config.callback, HttpCallbackHandler())
    logging.info("Executing commands in job mode")
    invoker.execute_all_commands()
    logging.info("Commands executed successfully")


def simulate_once(config_path: str, preset_value: Optional[str]) -> None:
    """Execute commands once with a logging-only callback handler. Used for simulate mode."""
    config = create_config(config_path)
    if preset_value is not None:
        for cmd in config.commands:
            if isinstance(cmd, TriggerCallbackOnChangedState):
                cmd._set_state(TriggerCallbackOnChangedState.STATE_KEY_CURRENT, preset_value)
                cmd._set_state(TriggerCallbackOnChangedState.STATE_KEY_PREVIOUS, preset_value)
    invoker = CommandInvoker(config.commands, config.callback, LoggingCallbackHandler())
    logging.info("Executing commands in simulate mode")
    invoker.execute_all_commands()
    logging.info("Simulate run complete")


def start_with_schedule(config_path: str) -> Thread:
    config = create_config(config_path)
    thread = Thread(target=schedule_process, args=(config, execute))
    thread.daemon = True
    thread.start()
    return thread


def shutdown() -> None:
    """Signal the background thread to stop gracefully."""
    _shutdown_event.set()


def execute(invoker: CommandInvoker) -> bool:
    logging.info("Executing commands")
    invoker.execute_all_commands()
    return False


def schedule_process(config: Config, func: Callable) -> None:
    invoker = CommandInvoker(config.commands, config.callback, HttpCallbackHandler())
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
            if _shutdown_event.wait(timeout=seconds_to_wait):
                logging.info("Shutdown requested, stopping scheduler")
                break

        if _shutdown_event.is_set():
            break

        stop = func(invoker)
        if stop:
            break

    logging.info("Scheduler stopped")

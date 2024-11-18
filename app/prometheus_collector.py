from enum import Enum
from datetime import datetime
from prometheus_client import Counter, Gauge
from prometheus_client.metrics import MetricWrapperBase


class ExecutionStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class CollectorManager:
    """
    Sets up and manages prometheus collectors.
    """
    _collectors = {}

    CALLBACK_EXECUTION = "callback_execution"
    COMMAND_EXECUTION = "command_execution"

    LAST_COMMAND_EXECUTION = "last_command_execution"
    NEXT_COMMAND_EXECUTION = "next_command_execution"

    @classmethod
    def register_collectors(cls):
        possible_states = [state for state in ExecutionStatus]

        cls._initialize_counter_with_labels(Counter(
            cls.CALLBACK_EXECUTION, "Counts number of performed callback calls", [
                "status"],
        ), possible_states)
        cls._initialize_counter_with_labels(Counter(
            cls.COMMAND_EXECUTION, "Counts failed command executions", [
                "status"]
        ), possible_states)

        cls._create_collector(Gauge(
            cls.LAST_COMMAND_EXECUTION, "Timestamp of the last command execution"
        ))

        cls._create_collector(Gauge(
            cls.NEXT_COMMAND_EXECUTION, "Timestamp of the next command execution"
        ))

    @classmethod
    def inc_callback_execution(cls, status: ExecutionStatus) -> None:
        cls._get_collector(cls.CALLBACK_EXECUTION).labels(
            status.value).inc()

    @classmethod
    def inc_command_execution(cls, status: ExecutionStatus) -> None:
        cls._get_collector(cls.COMMAND_EXECUTION).labels(
            status.value).inc()

    @classmethod
    def set_last_command_execution(cls, timestamp: datetime) -> None:
        cls._get_collector(cls.LAST_COMMAND_EXECUTION).set(timestamp.timestamp())

    @classmethod
    def set_next_command_execution(cls, timestamp: datetime) -> None:
        cls._get_collector(cls.NEXT_COMMAND_EXECUTION).set(timestamp.timestamp())

    @classmethod
    def _get_collector(cls, collector_name: str) -> MetricWrapperBase:
        return cls._collectors[collector_name]

    @classmethod
    def _create_collector(cls, collector: MetricWrapperBase) -> None:
        cls._collectors[collector._name] = collector

    @classmethod
    def _initialize_with_zero(cls, collector: MetricWrapperBase, flags: list[ExecutionStatus]) -> None:
        for flag in flags:
            collector.labels(flag.value).inc(0)

    @classmethod
    def _initialize_counter_with_labels(cls, collector: MetricWrapperBase, labels: list[str]) -> None:
        cls._create_collector(collector)
        cls._initialize_with_zero(collector, labels)

from enum import Enum
from prometheus_client import Counter
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

    @classmethod
    def register_collectors(cls):
        cls._create_collector(Counter(
            cls.CALLBACK_EXECUTION, "Counts number of performed callback calls", [
                "status"]
        ))
        cls._create_collector(Counter(
            cls.COMMAND_EXECUTION, "Counts failed command executions", [
                "status"]
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
    def _get_collector(cls, collector_name: str) -> MetricWrapperBase:
        return cls._collectors[collector_name]

    @classmethod
    def _create_collector(cls, collector: MetricWrapperBase) -> None:
        cls._collectors[collector._name] = collector

import logging
import os
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

_LogRecordFactory = Callable[..., logging.LogRecord]
_Event = dict[str, Any]
_ExtraFactory = Callable[[_Event], dict[str, Any]]


class LogRecordFactory:
    def __init__(self, wrapped_factory: _LogRecordFactory, extra: _Event):
        self.wrapped_factory = wrapped_factory
        self.extra = extra

    def __call__(self, *args: Any, **kwargs: Any) -> logging.LogRecord:
        record = self.wrapped_factory(*args, **kwargs)
        for key, value in self.extra.items():
            setattr(record, key, value)
        return record


def _build_cumulus_extras_from_cma(event: _Event) -> dict[str, Any]:
    if "cma" in event:
        event = event["cma"].get("event") or {}

    return {
        "cirrus_daac_version": os.getenv("DAAC_VERSION"),
        "cirrus_core_version": os.getenv("CORE_VERSION"),
        "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
        "granule_name": event.get("payload", {}).get("granules", [{}])[0].get("granuleId"),
        "workflow_execution_name": event.get("cumulus_meta", {}).get("execution_name"),
    }


def init_custom_log_record_factory(
    event: _Event,
    extra_factory: _ExtraFactory = _build_cumulus_extras_from_cma,
) -> None:
    """Configures the logging record factory and can be overwritten by providing
    a function that takes the event dict as an input and returns a dict of log
    records. Relies on the JSON formatter setting provided by AWS.

    By default the callable returns:
    {
        "cirrus_daac_version": os.getenv("DAAC_VERSION"),
        "cirrus_core_version": os.getenv("CORE_VERSION"),
        "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
        "granule_name": event.get("payload", {}).get("granules", [{}])[0].get("granuleId"),
        "workflow_execution_name": event.get("cumulus_meta", {}).get("execution_name"),
    }
    """
    extra = extra_factory(event)
    original_record_factory = logging.getLogRecordFactory()

    if isinstance(original_record_factory, LogRecordFactory):
        original_record_factory.extra = extra
    else:
        record_factory = LogRecordFactory(original_record_factory, extra)
        logging.setLogRecordFactory(record_factory)


def init_root_logger() -> None:
    """Set up log levels for lambda using the environment variable"""
    level = os.getenv("LOG_LEVEL", logging.INFO)

    logging.getLogger().setLevel(level)
    logging.getLogger("boto3").setLevel(logging.INFO)
    logging.getLogger("botocore").setLevel(logging.INFO)
    logging.getLogger("s3fs").setLevel(logging.INFO)


@contextmanager
def log_errors(*exceptions: type[BaseException]) -> Generator[None]:
    exceptions = exceptions or (BaseException,)
    try:
        yield
    except exceptions as e:
        logging.exception("%s: %s", e.__class__.__name__, e)
        raise

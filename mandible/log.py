import logging
import os
from collections.abc import Callable
from contextlib import contextmanager


def _build_cumulus_extras_from_cma(event: dict) -> dict:
    event = event.get("cma", {}).get("event", {})
    return {
        "cirrus_daac_version": os.getenv("DAAC_VERSION"),
        "cirrus_core_version": os.getenv("CORE_VERSION"),
        "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
        "granule_name": event.get("payload", {}).get("granules", [{}])[0].get("granuleId"),
        "workflow_execution_name": event.get("cumulus_meta", {}).get("execution_name"),
    }


def init_custom_log_record_factory(
    event: dict,
    record_builder: Callable[[dict], dict] = _build_cumulus_extras_from_cma,
) -> None:
    """
        configures the logging record factory and can be overwritten by providing a function that takes the event dict
        as an input and returns a dict of log records.
        Relies on the JSON formatter setting provided by AWS.
        By default the callable returns:
        {
            "cirrus_daac_version": os.getenv("DAAC_VERSION"),
            "cirrus_core_version": os.getenv("CORE_VERSION"),
            "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
            "granule_name": event.get("payload", {}).get("granules", [{}])[0].get("granuleId"),
            "workflow_execution_name": event.get("cumulus_meta", {}).get("execution_name"),
        }
    """
    extra = record_builder(event)
    original_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = original_factory(*args, **kwargs)
        for key, value in extra.items():
            setattr(record, key, value)
        return record
    logging.setLogRecordFactory(record_factory)


def init_root_logger():
    """Set up log levels for lambda using the environment variable"""
    level = os.getenv("LOG_LEVEL", logging.INFO)

    logging.getLogger().setLevel(level)
    logging.getLogger("boto3").setLevel(logging.INFO)
    logging.getLogger("botocore").setLevel(logging.INFO)
    logging.getLogger("s3fs").setLevel(logging.INFO)


@contextmanager
def log_errors(*exceptions: type[BaseException]):
    exceptions = exceptions or (BaseException,)
    try:
        yield
    except exceptions as e:
        logging.exception("%s: %s", e.__class__.__name__, e)
        raise

import json
import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Type


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "aws_request_id": getattr(record, "aws_request_id", None),
            "cirrus_core_version": getattr(record, "cirrus_core_version", None),
            "cirrus_daac_version": getattr(record, "cirrus_daac_version", None),
            "cumulus_version": getattr(record, "cumulus_version", None),
            "function_name": getattr(record, "function_name", None),
            "granule_name": getattr(record, "granule_name", None),
            "invoked_function_arn": getattr(record, "invoked_function_arn", None),
            "level": record.levelname,
            "log_group_name": getattr(record, "log_group_name", None),
            "log_stream_name": getattr(record, "log_stream_name", None),
            "memory_limit_in_mb": getattr(record, "memory_limit_in_mb", None),
            "message": record.getMessage(),
            "step_function_name": getattr(record, "step_function_name", None),
            "time": self.formatTime(record, self.datefmt),

        }
        return json.dumps(log_record)


def log_with_extra(func):
    @wraps(func)
    def wrapper(event, context, *args, **kwargs):
        extra = inject_cumulus_extras(event, context)
        # Inject context into the logger
        original_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = original_factory(*args, **kwargs)
            for key, value in extra.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return func(event, context, *args, **kwargs)
    return wrapper


def inject_cumulus_extras(event: dict, context: dict) -> dict:
    event = event.get("cma", {}).get("event", {})
    return {
        "aws_request_id": context.aws_request_id,
        "cirrus_daac_version": os.getenv("DAAC_VERSION"),
        "cirrus_core_version": os.getenv("CORE_VERSION"),
        "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
        "function_name": context.function_name,
        "granule_name": event.get("payload", {}).get("granules", [{}])[0].get("granuleId"),
        "invoked_function_arn": context.invoked_function_arn,
        "log_group_name": context.log_group_name,
        "log_stream_name": context.log_stream_name,
        "memory_limit_in_mb": context.memory_limit_in_mb,
        "step_function_name": event.get("cumulus_meta", {}).get("execution_name"),
    }


def init_root_logger():
    """Set up log levels for lambda using the environment variable"""
    level = os.getenv("LOG_LEVEL", logging.INFO)

    logging.getLogger().setLevel(level)
    logging.getLogger("boto3").setLevel(logging.INFO)
    logging.getLogger("botocore").setLevel(logging.INFO)
    logging.getLogger("s3fs").setLevel(logging.INFO)


@contextmanager
def log_errors(*exceptions: Type[BaseException]):
    exceptions = exceptions or (BaseException,)
    try:
        yield
    except exceptions as e:
        logging.exception("%s: %s", e.__class__.__name__, e)
        raise

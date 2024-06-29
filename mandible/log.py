import json
import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Type


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "message": record.getMessage(),
            "level": record.levelname,
            "time": self.formatTime(record, self.datefmt),
            "function_name": getattr(record, "function_name", None),
            "memory_limit_in_mb": getattr(record, "memory_limit_in_mb", None),
            "invoked_function_arn": getattr(record, "invoked_function_arn", None),
            "aws_request_id": getattr(record, "aws_request_id", None),
            "log_group_name": getattr(record, "log_group_name", None),
            "log_stream_name": getattr(record, "log_stream_name", None),
            "cumulus_version": getattr(record, "cumulus_version", None),
            "step_function_name": getattr(record, "step_function_name", None),
            "granule_name": getattr(record, "granule_name", None),
            "core_version": getattr(record, "core_version", None),
            "daac_version": getattr(record, "daac_version", None)
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
    return {
        "daac_version": os.getenv("DAAC_VERSION"),
        "core_version": os.getenv("CORE_VERSION"),
        "step_function_name": event.get("cma", {}).get("event", {}).get("cumulus_meta", {}).get("execution_name"),
        "cumulus_version": event.get("cma", {}).get("event", {}).get("cumulus_meta", {}).get("cumulus_version"),
        "granule_name": event.get("cma", {}).get("event", {}.get("payload"), {}).get("granules", [{}])[0].get("granuleId"),
        "aws_request_id": context.aws_request_id,
        "function_name": context.function_name,
        "memory_limit_in_mb": context.memory_limit_in_mb,
        "invoked_function_arn": context.invoked_function_arn,
        "log_group_name": context.log_group_name,
        "log_stream_name": context.log_stream_name,
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

import json
import logging
import os
from contextlib import contextmanager
from functools import wraps
from typing import Type


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "line_no": record.lineno,
            "exception": self.formatException(record.exc_info) if record.exc_info else None,
            "extra": record.__dict__.get("extra", {})
        }
        return json.dumps(log_record)


def log_with_extra(extra=None):
    if extra is not None and not (isinstance(extra, dict) or callable(extra)):
        raise TypeError("Extra must be a dictionary or callable.")

    def decorator(func):
        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            kwargs = {"extra": {}}
            if callable(extra):
                kwargs["extra"].update(extra(event, context))
            else:
                kwargs["extra"] = extra

            original_factory = logging.getLogRecordFactory()

            def record_factory(*args, **kwargs):
                record = original_factory(*args, **kwargs)
                for key, value in kwargs["extra"].items():
                    setattr(record, key, value)
                return record

            logging.setLogRecordFactory(record_factory)
            return func(event, context, *args, **kwargs)
        return wrapper
    return decorator


def inject_cumulus_extras(event: dict, context: dict) -> dict:
    return {
        "daac_version": os.getenv("DAAC_VERSION"),
        "core_Version": os.getenv("CORE_VERSION"),
        "step_function_name": event.get("cumulus_meta", {}).get("execution_name"),
        "cumulus_version": event.get("cumulus_meta", {}).get("cumulus_version"),
        "aws_request_id": context.aws_request_id,
        "function_name": context.function_name,
        "memory_limit_in_mb": context.memory_limit_in_mb,
        "invoked_function_arn": context.invoked_function_arn,
        "log_group_name": context.log_group_name,
        "log_stream_name": context.log_stream_name,
    }


def init_json_formatter():
    log = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    log.addHandler(handler)


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

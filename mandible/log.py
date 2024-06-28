import json
import logging
import os
from contextlib import contextmanager
from typing import Type

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'message': record.getMessage(),
            'line_no': record.lineno,
            'exception': self.formatException(record.exc_info) if record.exc_info else None,
            'extra': record.__dict__.get('extra', {})
        }
        return json.dumps(log_record)



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

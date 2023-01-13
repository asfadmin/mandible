import logging
import os
from contextlib import contextmanager
from typing import Type


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

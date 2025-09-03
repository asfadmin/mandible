from dataclasses import dataclass
from typing import IO

from mandible.metadata_mapper.context import Context

from .storage import Storage


@dataclass
class _PlaceholderBase(Storage, register=False):
    """
    Base class for defining placeholder implementations for classes that
    require extra dependencies to be installed
    """

    def __init__(self, dep: str):
        raise Exception(
            f"{dep} must be installed to use the {self.__class__.__name__} format class",
        )

    def open_file(self, context: Context) -> IO[bytes]:
        # __init__ always raises
        raise RuntimeError("Unreachable!")


@dataclass
class CmrQuery(_PlaceholderBase):
    def __init__(self) -> None:
        super().__init__("requests")


@dataclass
class HttpRequest(_PlaceholderBase):
    def __init__(self) -> None:
        super().__init__("requests")


@dataclass
class S3File(_PlaceholderBase):
    def __init__(self) -> None:
        super().__init__("s3fs")

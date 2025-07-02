import contextlib
from dataclasses import dataclass
from typing import IO, Any

from mandible.metadata_mapper.key import Key

from .format import FileFormat


@dataclass
class _PlaceholderBase(FileFormat[None], register=False):
    """Base class for defining placeholder implementations for classes that
    require extra dependencies to be installed.
    """
    def __init__(self, dep: str):
        raise Exception(
            f"{dep} must be installed to use the {self.__class__.__name__} "
            "format class",
        )

    @staticmethod
    def parse_data(file: IO[bytes]) -> contextlib.AbstractContextManager[None]:
        # __init__ always raises
        raise RuntimeError("Unreachable!")

    @staticmethod
    def eval_key(data: None, key: Key) -> Any:
        # __init__ always raises
        raise RuntimeError("Unreachable!")


@dataclass
class H5(_PlaceholderBase):
    def __init__(self) -> None:
        super().__init__("h5py")


@dataclass
class Xml(_PlaceholderBase):
    def __init__(self) -> None:
        super().__init__("lxml")

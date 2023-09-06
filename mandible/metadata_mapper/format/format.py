import contextlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, Any, ContextManager, Dict, Iterable, Type


class FormatError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason


FORMAT_REGISTRY: Dict[str, Type["Format"]] = {}


@dataclass
class Format(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True):
        if register:
            FORMAT_REGISTRY[cls.__name__] = cls

    # Begin class definition
    def get_values(self, file: IO[bytes], keys: Iterable[str]):
        with self._parse_data(file) as data:
            return {
                key: self._eval_key_wrapper(data, key)
                for key in keys
            }

    def _eval_key_wrapper(self, data, key: str):
        try:
            return self._eval_key(data, key)
        except KeyError as e:
            raise FormatError(f"key not found '{key}'") from e
        except Exception as e:
            raise FormatError(f"'{key}' {e}") from e

    @staticmethod
    @abstractmethod
    def _parse_data(file: IO[bytes]) -> ContextManager[Any]:
        pass

    @staticmethod
    @abstractmethod
    def _eval_key(data, key: str):
        pass


# Define placeholders for when extras are not installed

class _PlaceholderBase(Format, register=False):
    """
    Base class for defining placeholder implementations for classes that
    require extra dependencies to be installed
    """
    def __init__(self, dep: str):
        raise Exception(
            f"{dep} must be installed to use the {self.__class__.__name__} "
            "format class"
        )

    @staticmethod
    def _parse_data(file: IO[bytes]) -> ContextManager[Any]:
        pass

    @staticmethod
    def _eval_key(data, key: str):
        pass


class H5(_PlaceholderBase):
    def __init__(self):
        super().__init__("h5py")


class Xml(_PlaceholderBase):
    def __init__(self):
        super().__init__("lxml")


# Define formats that don't require extra dependencies

class Json(Format):
    @staticmethod
    @contextlib.contextmanager
    def _parse_data(file: IO[bytes]):
        yield json.load(file)

    @staticmethod
    def _eval_key(data: dict, key: str):
        val = data
        for key in key.split("."):
            val = val[key]

        return val

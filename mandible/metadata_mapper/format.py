import contextlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, Any, ContextManager, Dict, Iterable, Type

from ..h5_parser import normalize

try:
    import h5py
except ImportError:
    h5py = None

try:
    from lxml import etree
except ImportError:
    etree = None


class FormatError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason


FORMAT_REGISTRY: Dict[str, Type["Format"]] = {}


@dataclass
class Format(ABC):
    # Registry boilerplate
    def __init_subclass__(cls):
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
            raise FormatError(f"Key not found '{key}'") from e
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


class H5(Format):
    def __init__(self) -> None:
        if h5py is None:
            raise Exception("h5py must be installed to use the H5 format class")

    @staticmethod
    @contextlib.contextmanager
    def _parse_data(file: IO[bytes]):
        with h5py.File(file, "r") as h5f:
            yield h5f

    @staticmethod
    def _eval_key(data, key: str):
        return normalize(data[key][()])


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


class Xml(Format):
    def __init__(self) -> None:
        if etree is None:
            raise Exception("lxml must be installed to use the Xml format class")

    @staticmethod
    @contextlib.contextmanager
    def _parse_data(file: IO[bytes]):
        yield etree.parse(file)

    @staticmethod
    def _eval_key(data: etree.ElementTree, key: str):
        elements = data.xpath(key)
        if not elements:
            raise KeyError(key)

        # TODO(reweeden): Add a way to return the whole list here and not just
        # the first element.
        return elements[0].text

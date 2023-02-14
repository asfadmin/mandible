import json
from abc import ABC, abstractmethod
from typing import IO, Dict, Iterable

from lxml import etree

from ..h5_parser import H5parser


class Format(ABC):
    _SUBCLASSES: Dict[str, "Format"] = {}

    def __init_subclass__(cls):
        Format._SUBCLASSES[cls.__name__] = cls

    @classmethod
    def get_subclass(cls, name: str) -> "Format":
        return cls._SUBCLASSES[name]

    @abstractmethod
    def get_values(self, file: IO[bytes], keys: Iterable[str]):
        pass


class H5(Format):
    def get_values(self, file: IO[bytes], keys: Iterable[str]):
        h5_data = H5parser(keys)
        h5_data.read_file(file)
        return h5_data


class Json(Format):
    def get_values(self, file: IO[bytes], keys: Iterable[str]):
        data = json.load(file)
        return {
            key: self._eval_key(data, key)
            for key in keys
        }

    @staticmethod
    def _eval_key(data: dict, key: str):
        val = data
        for key in key.split("."):
            val = val[key]

        return val


class Xml(Format):
    def get_values(self, file: IO[bytes], keys: Iterable[str]):
        tree = etree.parse(file)
        return {
            key: tree.xpath(key)[0].text
            for key in keys
        }

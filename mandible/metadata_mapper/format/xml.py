import contextlib
from dataclasses import dataclass
from typing import IO, Any

from lxml import etree

from mandible.metadata_mapper.key import Key

from .format import FileFormat


@dataclass
class Xml(FileFormat):
    @staticmethod
    @contextlib.contextmanager
    def parse_data(file: IO[bytes]) -> Any:
        yield etree.parse(file)

    @staticmethod
    def eval_key(data: etree.ElementTree, key: Key) -> Any:
        nsmap = data.getroot().nsmap
        elements = data.xpath(key.key, namespaces=nsmap)
        values = [element.text for element in elements]

        return key.resolve_list_match(values)

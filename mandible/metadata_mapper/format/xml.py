import contextlib
from collections.abc import Generator, Iterable
from dataclasses import dataclass
from typing import IO, Any, Union

from lxml import etree

from mandible.metadata_mapper.key import Key

from .format import FileFormat


@dataclass
class Xml(FileFormat[etree._ElementTree]):
    @staticmethod
    @contextlib.contextmanager
    def parse_data(file: IO[bytes]) -> Generator[etree._ElementTree]:
        yield etree.parse(file)

    @staticmethod
    def eval_key(data: etree._ElementTree, key: Key) -> Any:
        nsmap = data.getroot().nsmap
        xpath_result = data.xpath(
            key.key,
            # Lxml type stubs don't handle None key for default namespaces
            namespaces=nsmap,  # type: ignore
        )
        if isinstance(xpath_result, Iterable):
            values = [convert_result(item) for item in xpath_result]

            return key.resolve_list_match(values)

        # Xpath supports functions such as `count` that can result in
        # `data.xpath` returning something other than a list of matches.
        return xpath_result


def convert_result(result: Union[etree._Element, int, str, bytes, tuple]):
    if isinstance(result, etree._Element):
        return result.text
    if isinstance(result, (int, str, bytes)):
        return result

    raise TypeError(f"Unsupported type {repr(result.__class__.__name__)}")

import contextlib
from typing import IO, Any

from lxml import etree

from .format import Format


class Xml(Format):
    @staticmethod
    @contextlib.contextmanager
    def _parse_data(file: IO[bytes]) -> Any:
        yield etree.parse(file)

    @staticmethod
    def _eval_key(data: etree.ElementTree, key: str):
        nsmap = data.getroot().nsmap
        elements = data.xpath(key, namespaces=nsmap)
        if not elements:
            raise KeyError(key)

        # TODO(reweeden): Add a way to return the whole list here and not just
        # the first element.
        return elements[0].text

from abc import ABC, abstractmethod
from typing import Callable, Dict, Union

from ..context import Context
from ..source import Source

Key = Union[str, Callable[[Context], str]]


def get_key(key: Key, context: Context) -> str:
    if callable(key):
        key = key(context)

    return key


class TemplateDirective(ABC):
    """Base class for directives in a metadata template.

    A directive is a special marker in the metadata template which will be
    replaced by the MetadataMapper.
    """

    def __init__(self, context: Context, sources: Dict[str, Source]):
        self.context = context
        self.sources = sources

    @abstractmethod
    def call(self):
        pass

    def prepare(self):
        pass

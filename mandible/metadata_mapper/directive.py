from abc import ABC, abstractmethod
from typing import Callable, Dict, Union

from .context import Context
from .exception import MetadataMapperError
from .source import Source


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


class Mapped(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """
    def __init__(
        self,
        context: Context,
        sources: Dict[str, Source],
        source: str,
        key: Union[str, Callable[[Context], str]]
    ):
        super().__init__(context, sources)

        if source not in sources:
            raise MetadataMapperError(f"source '{source}' does not exist")

        self.source = sources[source]
        if callable(key):
            key = key(context)
        self.key = key

    def call(self):
        return self.source.get_value(self.key)

    def prepare(self):
        self.source.add_key(self.key)



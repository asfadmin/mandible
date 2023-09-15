import io
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Union

from .context import Context
from .exception import MetadataMapperError
from .format import FORMAT_REGISTRY
from .source import Source

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
        key: Key
    ):
        super().__init__(context, sources)

        if source not in sources:
            raise MetadataMapperError(f"source '{source}' does not exist")

        self.source = sources[source]
        self.key = get_key(key, context)

    def call(self):
        return self.source.get_value(self.key)

    def prepare(self):
        self.source.add_key(self.key)


class Reformatted(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """
    def __init__(
        self,
        context: Context,
        sources: Dict[str, Source],
        format: str,
        value: Any,
        key: Key
    ):
        super().__init__(context, sources)

        format_cls = FORMAT_REGISTRY.get(format)
        if format_cls is None:
            raise MetadataMapperError(f"format '{format}' does not exist")

        self.format = format_cls()
        self.value = value
        self.key = get_key(key, context)

    def call(self):
        if isinstance(self.value, bytes):
            value = self.value
        elif isinstance(self.value, str):
            value = self.value.encode()
        else:
            raise MetadataMapperError(
                "value must be of type 'bytes' or 'str' but got "
                f"'{type(self.value).__name__}'"
            )

        return self.format.get_value(
            io.BytesIO(value),
            self.key
        )

import io
from typing import Any, Dict

from ..context import Context
from ..exception import MetadataMapperError
from ..format import FORMAT_REGISTRY
from ..source import Source
from .directive import Key, TemplateDirective, get_key


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
                f"'{type(self.value).__name__}'",
            )

        return self.format.get_value(
            io.BytesIO(value),
            self.key
        )

import io
from dataclasses import dataclass
from typing import Any

from ..exception import MetadataMapperError
from ..format import FORMAT_REGISTRY
from .directive import Key, TemplateDirective, get_key


@dataclass
class Reformatted(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """

    format: str
    value: Any
    key: Key

    def __post_init__(self):
        format_cls = FORMAT_REGISTRY.get(self.format)
        if format_cls is None:
            raise MetadataMapperError(f"format '{self.format}' does not exist")

        self.format_obj = format_cls()
        self.key_str = get_key(self.key, self.context)

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

        return self.format_obj.get_value(
            io.BytesIO(value),
            self.key_str,
        )

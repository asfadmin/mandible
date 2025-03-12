import io
from dataclasses import dataclass, field
from typing import Any

from mandible.metadata_mapper.exception import MetadataMapperError
from mandible.metadata_mapper.format import FORMAT_REGISTRY
from mandible.metadata_mapper.types import Key, Template

from .directive import TemplateDirective, get_key


@dataclass
class Reformatted(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """

    format: str
    value: Any
    key: Key
    key_options: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        format_cls = FORMAT_REGISTRY.get(self.format)
        if format_cls is None:
            raise MetadataMapperError(f"format {repr(self.format)} does not exist")

        self.format_obj = format_cls()
        self.key_obj = get_key(self.key, self.context, self.key_options)

    def call(self) -> Template:
        if isinstance(self.value, bytes):
            value = self.value
        elif isinstance(self.value, str):
            value = self.value.encode()
        else:
            raise MetadataMapperError(
                "value must be of type 'bytes' or 'str' but got "
                f"{repr(type(self.value).__name__)}",
            )

        return self.format_obj.get_value(
            io.BytesIO(value),
            self.key_obj,
        )

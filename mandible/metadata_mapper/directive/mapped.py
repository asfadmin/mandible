from dataclasses import dataclass, field

from mandible.metadata_mapper.exception import MetadataMapperError
from mandible.metadata_mapper.types import Key

from .directive import TemplateDirective, get_key


@dataclass
class Mapped(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """

    source: str
    key: Key
    key_options: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.source not in self.sources:
            raise MetadataMapperError(f"source {repr(self.source)} does not exist")

        self.source_obj = self.sources[self.source]
        self.key_obj = get_key(self.key, self.context, self.key_options)

    def call(self):
        return self.source_obj.get_value(self.key_obj)

    def prepare(self):
        self.source_obj.add_key(self.key_obj)

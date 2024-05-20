from dataclasses import dataclass

from ..exception import MetadataMapperError
from ..types import Key
from .directive import TemplateDirective, get_key


@dataclass
class Mapped(TemplateDirective):
    """A value mapped to the template from a metadata Source.

    The directive will be replaced by looking at the specified Source and
    extracting the defined key.
    """

    source: str
    key: Key

    def __post_init__(self):
        if self.source not in self.sources:
            raise MetadataMapperError(f"source '{self.source}' does not exist")

        self.source_obj = self.sources[self.source]
        self.key_str = get_key(self.key, self.context)

    def call(self):
        return self.source_obj.get_value(self.key_str)

    def prepare(self):
        self.source_obj.add_key(self.key_str)

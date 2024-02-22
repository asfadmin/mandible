from typing import Dict

from ..context import Context
from ..exception import MetadataMapperError
from ..source import Source
from .directive import Key, TemplateDirective, get_key


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

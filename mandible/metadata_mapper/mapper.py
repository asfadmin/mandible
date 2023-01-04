import logging
from dataclasses import dataclass, field
from typing import Dict

from .source import Source, SourceProvider

log = logging.getLogger(__name__)


@dataclass
class Context:
    files: Dict[str, Dict] = field(default_factory=dict)


class MetadataMapper:
    def __init__(self, template, source_provider: SourceProvider = None):
        self.template = template
        self.source_provider = source_provider

    def get_metadata(self, context: Context) -> Dict:
        if self.source_provider is not None:
            sources = self.source_provider.get_sources()
        else:
            sources = {}
        self._cache_source_keys(sources)

        for name, source in sources.items():
            log.info("Querying source '%s': %s", name, source)
            try:
                source.query_all_values(context)
            except Exception as e:
                raise RuntimeError(f"Failed to query source '{name}'") from e

        return self._replace_template(self.template, sources)

    def _cache_source_keys(self, sources: Dict[str, Source]):
        for value in _walk_values(self.template):
            if isinstance(value, dict) and "@mapped" in value:
                config = value["@mapped"]
                source = config["source"]
                key = config["key"]

                sources[source].add_key(key)

    def _replace_template(self, template, sources: Dict[str, Source]):
        if isinstance(template, dict):
            # TODO(reweeden): Implement functions as objects dynamically
            if "@mapped" in template:
                config = template["@mapped"]
                source = config["source"]
                key = config["key"]

                return sources[source].get_value(key)
            return {
                k: self._replace_template(v, sources)
                for k, v in template.items()
            }
        if isinstance(template, list):
            return [self._replace_template(v, sources) for v in template]
        return template


def _walk_values(obj):
    yield obj
    if isinstance(obj, dict):
        for val in obj.values():
            yield from _walk_values(val)
    elif isinstance(obj, (list, tuple, set)):
        for val in obj:
            yield from _walk_values(val)

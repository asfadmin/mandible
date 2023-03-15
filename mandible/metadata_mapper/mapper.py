import logging
from typing import Dict, Tuple

from .context import Context
from .source import Source, SourceProvider

log = logging.getLogger(__name__)


class MetadataMapperError(Exception):
    pass


class MetadataMapper:
    def __init__(self, template, source_provider: SourceProvider = None):
        self.template = template
        self.source_provider = source_provider

    def get_metadata(self, context: Context) -> Dict:
        if self.source_provider is not None:
            sources = self.source_provider.get_sources()
        else:
            sources = {}

        try:
            self._cache_source_keys(context, sources)
        except Exception as e:
            raise MetadataMapperError(
                f"failed to process template: {e}"
            )

        for name, source in sources.items():
            log.info("Querying source '%s': %s", name, source)
            try:
                source.query_all_values(context)
            except Exception as e:
                raise MetadataMapperError(
                    f"failed to query source '{name}': {e}"
                ) from e

        try:
            return self._replace_template(context, self.template, sources)
        except Exception as e:
            raise MetadataMapperError(
                f"failed to evaluate template: {e}"
            ) from e

    def _cache_source_keys(self, context: Context, sources: Dict[str, Source]):
        for value in _walk_values(self.template):
            if isinstance(value, dict) and "@mapped" in value:
                source, key = self._get_mapped_key(value, context)
                sources[source].add_key(key)

    def _replace_template(self, context: Context, template, sources: Dict[str, Source]):
        if isinstance(template, dict):
            # TODO(reweeden): Implement functions as objects dynamically
            if "@mapped" in template:
                source, key = self._get_mapped_key(template, context)
                return sources[source].get_value(key)

            return {
                k: self._replace_template(context, v, sources)
                for k, v in template.items()
            }
        if isinstance(template, list):
            return [self._replace_template(context, v, sources) for v in template]
        return template

    def _get_mapped_key(self, value: dict, context: Context) -> Tuple[str, str]:
        config = value["@mapped"]
        source = config.get("source")
        if source is None:
            raise MetadataMapperError("@mapped attribute missing key 'source'")

        key = config.get("key")
        if key is None:
            raise MetadataMapperError("@mapped attribute missing key 'key'")

        if callable(key):
            key = key(context)

        return source, key


def _walk_values(obj):
    yield obj
    if isinstance(obj, dict):
        for val in obj.values():
            yield from _walk_values(val)
    elif isinstance(obj, (list, tuple, set)):
        for val in obj:
            yield from _walk_values(val)

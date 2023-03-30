import logging
from typing import Dict, Tuple

from .context import Context
from .source import Source, SourceProvider

log = logging.getLogger(__name__)


class MetadataMapperError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


class TemplateError(MetadataMapperError):
    def __init__(self, msg: str, debug_path: str = None):
        super().__init__(msg)
        self.debug_path = debug_path

    def __str__(self) -> str:
        debug = ""
        if self.debug_path is not None:
            debug = f" at {self.debug_path}"

        return f"failed to process template{debug}: {self.msg}"


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
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to cache source keys: {e}"
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
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to evaluate template: {e}"
            ) from e

    def _cache_source_keys(self, context: Context, sources: Dict[str, Source]):
        for value, debug_path in _walk_values(self.template):
            if isinstance(value, dict) and "@mapped" in value:
                source, key = self._get_mapped_key(value, context, debug_path)
                sources[source].add_key(key)

    def _replace_template(
        self,
        context: Context,
        template,
        sources: Dict[str, Source],
        debug_path: str = "$",
    ):
        if isinstance(template, dict):
            # TODO(reweeden): Implement functions as objects dynamically
            if "@mapped" in template:
                source, key = self._get_mapped_key(template, context, debug_path)
                return sources[source].get_value(key)

            return {
                k: self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}.{k}",
                )
                for k, v in template.items()
            }
        if isinstance(template, list):
            return [
                self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}[{i}]",
                )
                for i, v in enumerate(template)
            ]
        return template

    def _get_mapped_key(self, value: dict, context: Context, debug_path: str) -> Tuple[str, str]:
        config = value["@mapped"]
        source = config.get("source")
        if source is None:
            raise TemplateError(
                "@mapped attribute missing key 'source'",
                debug_path
            )

        key = config.get("key")
        if key is None:
            raise TemplateError(
                "@mapped attribute missing key 'key'",
                debug_path
            )

        if callable(key):
            key = key(context)

        return source, key


def _walk_values(obj, debug_path: str = "$"):
    yield obj, debug_path
    if isinstance(obj, dict):
        for key, val in obj.items():
            yield from _walk_values(val, f"{debug_path}.{key}")
    elif isinstance(obj, (list, tuple, set)):
        for i, val in enumerate(obj):
            yield from _walk_values(val, f"{debug_path}[{i}]")

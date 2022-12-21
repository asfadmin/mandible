import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Set

from .format import Format
from .storage import Storage

log = logging.getLogger(__name__)


@dataclass
class Context:
    files: Dict[str, Dict] = field(default_factory=dict)


class Source:
    def __init__(
        self,
        storage: Storage,
        format: Format,
    ):
        self.storage = storage
        self.format = format

        self._keys: Set[str] = set()
        self._values: Dict[str] = {}

    def add_key(self, key: str):
        self._keys.add(key)

    def query_all_values(self):
        with self.storage.get_file() as file:
            self._values.update(
                self.format.get_values(
                    file,
                    list(self._keys)
                )
            )

    def get_value(self, key: str):
        return self._values[key]


class SourceProvider(ABC):
    @abstractmethod
    def get_sources(self, context: Context) -> Dict[str, Source]:
        pass


class ConfigSourceProvider(SourceProvider):
    """Provide sources from JSON object config"""

    def __init__(self, config: Dict):
        self.config = config

    def get_sources(self, context: Context) -> Dict[str, Source]:
        return {
            key: Source(
                storage=self._get_storage(key, config["storage"], context),
                format=self._get_format(config["format"])
            )
            for key, config in self.config.items()
        }

    def _get_storage(self, name: str, config: Dict, context: Context) -> Storage:
        cls = Storage.get_subclass(config["class"])

        if (file_name := config.get("name")) is not None:
            file = context.files[file_name]
        elif (file_name_match := config.get("name_match")) is not None:
            pattern = re.compile(file_name_match)
            for file_name, file_info in context.files.items():
                if pattern.match(file_name):
                    file = file_info
                    break
            else:
                raise RuntimeError(
                    f"No files matched pattern '{file_name_match}'"
                )
        else:
            raise ValueError(
                f"Missing 'name' or 'name_match' keys for source '{name}'"
            )

        return cls(**file)

    def _get_format(self, config: Dict) -> Format:
        cls_name = config["class"]
        cls = Format.get_subclass(cls_name)
        return cls()


class MetadataMapper:
    def __init__(self, template, source_provider: SourceProvider = None):
        self.template = template
        self.source_provider = source_provider

    def get_metadata(self, context: Context) -> Dict:
        if self.source_provider is not None:
            sources = self.source_provider.get_sources(context)
        else:
            sources = {}
        self._cache_source_keys(sources)

        for name, source in sources.items():
            log.info("Querying source '%s': %s", name, source)
            source.query_all_values()

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

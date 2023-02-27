import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Set

from .context import Context
from .format import Format
from .storage import Storage

log = logging.getLogger(__name__)


@dataclass
class Source:
    storage: Storage
    format: Format

    def __post_init__(self):
        self._keys: Set[str] = set()
        self._values: Dict[str, Any] = {}

    def add_key(self, key: str):
        self._keys.add(key)

    def query_all_values(self, context: Context):
        with self.storage.open_file(context) as file:
            keys = list(self._keys)
            new_values = self.format.get_values(file, keys)
            log.debug(
                "%s: using keys %s, got new values %s",
                self,
                keys,
                new_values
            )
            self._values.update(new_values)

    def get_value(self, key: str):
        return self._values[key]


class SourceProvider(ABC):
    @abstractmethod
    def get_sources(self) -> Dict[str, Source]:
        pass


class PySourceProvider(SourceProvider):
    """Dummy provider that passes sources through as a python object"""

    def __init__(self, sources: Dict[str, Source]):
        self.sources = sources

    def get_sources(self) -> Dict[str, Source]:
        return self.sources


class ConfigSourceProvider(SourceProvider):
    """Provide sources from JSON object config"""

    def __init__(self, config: Dict):
        self.config = config

    def get_sources(self) -> Dict[str, Source]:
        return {
            key: Source(
                storage=self._get_storage(key, config["storage"]),
                format=self._get_format(config["format"])
            )
            for key, config in self.config.items()
        }

    def _get_storage(self, name: str, config: Dict) -> Storage:
        cls = Storage.get_subclass(config["class"])
        name = config.get("name")
        name_match = config.get("name_match")

        return cls(
            name=name,
            name_match=name_match
        )

    def _get_format(self, config: Dict) -> Format:
        cls_name = config["class"]
        cls = Format.get_subclass(cls_name)
        return cls()

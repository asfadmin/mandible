import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Set, Type, TypeVar

from mandible.internal import Registry

from .context import Context
from .format import FORMAT_REGISTRY, Format
from .storage import STORAGE_REGISTRY, Storage

log = logging.getLogger(__name__)

T = TypeVar("T")


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
        if not self._keys:
            return

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
        # TODO(reweeden): Catch errors and correlate to key
        return {
            key: Source(
                storage=self._get_registered_class(STORAGE_REGISTRY, config["storage"]),
                format=self._get_registered_class(FORMAT_REGISTRY, config["format"])
            )
            for key, config in self.config.items()
        }

    def _get_registered_class(
        self,
        registry: Registry[Type[T]],
        config: Dict[str, Any]
    ) -> T:
        cls_name = config["class"]
        cls = registry[cls_name]

        kwargs = {
            k: v
            for k, v in config.items()
            if k != "class"
        }

        return cls(**kwargs)

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Set, Type, TypeVar

from mandible.internal import Registry

from .context import Context
from .format import FORMAT_REGISTRY, Format
from .key import Key
from .storage import STORAGE_REGISTRY, Storage

log = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class Source:
    storage: Storage
    format: Format

    def __post_init__(self):
        self._keys: Set[Key] = set()
        self._values: Dict[Key, Any] = {}

    def add_key(self, key: Key):
        self._keys.add(key)

    def query_all_values(self, context: Context):
        if not self._keys:
            return

        with self.storage.open_file(context) as file:
            keys = list(self._keys)
            new_values = self.format.get_values(file, keys)
            log.debug(
                "%s: using keys %r, got new values %r",
                self,
                keys,
                new_values
            )
            self._values.update(new_values)

    def get_value(self, key: Key):
        return self._values[key]


class SourceProviderError(Exception):
    pass


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
            key: self._create_source(key, config)
            for key, config in self.config.items()
        }

    def _create_source(self, key: str, config: Dict) -> Source:
        try:
            return Source(
                storage=self._create_from_registry(
                    STORAGE_REGISTRY,
                    config,
                    "storage"
                ),
                format=self._create_from_registry(
                    FORMAT_REGISTRY,
                    config,
                    "format"
                )
            )
        except Exception as e:
            raise SourceProviderError(
                f"failed to create source {repr(key)}: {e}",
            ) from e

    def _create_from_registry(
        self,
        registry: Registry[Type[T]],
        config: Dict[str, Any],
        name_key: str
    ) -> T:
        class_config = config.get(name_key)
        if class_config is None:
            raise SourceProviderError(f"missing key {repr(name_key)} in config")

        cls_name = class_config.get("class")
        if cls_name is None:
            raise SourceProviderError(
                f"missing key 'class' in config {class_config}"
            )

        cls = registry.get(cls_name)
        if cls is None:
            raise SourceProviderError(f"invalid {name_key} type {repr(cls_name)}")

        return self._create_class(cls, class_config)

    def _create_class(self, cls: Type[T], config: Dict[str, Any]) -> T:
        kwargs = {
            k: self._convert_arg(k, v)
            for k, v in config.items()
            if k != "class"
        }

        return cls(**kwargs)

    def _convert_arg(self, name_key: str, arg: Any) -> Any:
        if isinstance(arg, dict) and "class" in arg:
            cls_name = arg["class"]

            # Only support Format classes for now
            format_cls = FORMAT_REGISTRY.get(cls_name)
            if format_cls:
                return self._create_class(format_cls, arg)

            raise SourceProviderError(f"invalid {name_key} type {repr(cls_name)}")

        return arg

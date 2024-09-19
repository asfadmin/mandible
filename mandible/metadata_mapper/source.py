import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, Type, TypeVar

from .context import Context
from .format import FORMAT_REGISTRY, Format
from .key import Key
from .storage import STORAGE_REGISTRY, Storage

log = logging.getLogger(__name__)

T = TypeVar("T")

SOURCE_REGISTRY: Dict[str, Type["Source"]] = {}

REGISTRY_TYPE_MAP = {
    "Format": FORMAT_REGISTRY,
    "Storage": STORAGE_REGISTRY,
    "Source": SOURCE_REGISTRY,
}


@dataclass
class Source(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True, **kwargs):
        if register:
            SOURCE_REGISTRY[cls.__name__] = cls

        super().__init_subclass__(**kwargs)

    # Begin class definition
    def __post_init__(self):
        self._keys: Set[Key] = set()
        self._values: Dict[Key, Any] = {}

    def add_key(self, key: Key):
        self._keys.add(key)

    @abstractmethod
    def query_all_values(self, context: Context):
        pass

    def get_value(self, key: Key):
        return self._values[key]


@dataclass
class FileSource(Source):
    storage: Storage
    format: Format

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
        cls_name = config.get("class") or FileSource.__name__
        cls = SOURCE_REGISTRY.get(cls_name)
        if cls is None:
            raise SourceProviderError(f"{key} invalid source type {repr(cls_name)}")

        try:
            return self._instantiate_class(cls, config)
        except Exception as e:
            raise SourceProviderError(
                f"failed to create source {repr(key)}: {e}",
            ) from e

    def _create_object(
        self,
        parent_cls: Type[Any],
        key: str,
        config: Dict,
    ) -> Any:
        cls_name = config.get("class")
        if cls_name is None:
            raise SourceProviderError(
                f"missing key 'class' in config {config}"
            )

        # TODO(reweeden): As of python3.10, inspect.get_annotations(parent_cls)
        # should be used instead here.
        base_cls = parent_cls.__annotations__[key]

        cls = self._get_class_from_registry(base_cls, cls_name)
        if cls is None:
            raise SourceProviderError(f"invalid {key} type {repr(cls_name)}")

        if not issubclass(cls, base_cls):
            raise SourceProviderError(
                f"invalid {key} type {repr(cls_name)} must be a subclass of "
                f"{repr(base_cls.__name__)}",
            )

        return self._instantiate_class(cls, config)

    def _get_class_from_registry(
        self,
        base_cls: Type[Any],
        cls_name: str,
    ) -> Optional[Type[Any]]:
        cls = REGISTRY_TYPE_MAP.get(base_cls.__name__, {}).get(cls_name)

        if cls is None:
            for parent_base_cls in base_cls.__mro__:
                cls = REGISTRY_TYPE_MAP.get(
                    parent_base_cls.__name__,
                    {},
                ).get(cls_name)
                if cls is not None:
                    break

        return cls

    def _instantiate_class(self, cls: Type[T], config: Dict[str, Any]) -> T:
        kwargs = {
            k: self._convert_arg(cls, k, v)
            for k, v in config.items()
            if k != "class"
        }

        return cls(**kwargs)

    def _convert_arg(self, parent_cls: Type[Any], key: str, arg: Any) -> Any:
        if isinstance(arg, dict) and "class" in arg:
            return self._create_object(parent_cls, key, arg)

        return arg

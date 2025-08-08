import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar

from .context import ContextValue
from .format import FORMAT_REGISTRY
from .source import SOURCE_REGISTRY, FileSource, Source
from .storage import STORAGE_REGISTRY

log = logging.getLogger(__name__)

T = TypeVar("T")

REGISTRY_TYPE_MAP: dict[str, dict[str, Any]] = {
    "Format": FORMAT_REGISTRY,
    "Source": SOURCE_REGISTRY,
    "Storage": STORAGE_REGISTRY,
}


class SourceProviderError(Exception):
    pass


class SourceProvider(ABC):
    @abstractmethod
    def get_sources(self) -> dict[str, Source]:
        pass


class PySourceProvider(SourceProvider):
    """Dummy provider that passes sources through as a python object"""

    def __init__(self, sources: dict[str, Source]):
        self.sources = sources

    def get_sources(self) -> dict[str, Source]:
        return self.sources


class ConfigSourceProvider(SourceProvider):
    """Provide sources from JSON object config"""

    def __init__(self, config: dict):
        self.config = config

    def get_sources(self) -> dict[str, Source]:
        return {
            key: self._create_source(key, config) for key, config in self.config.items()
        }

    def _create_source(self, key: str, config: dict) -> Source:
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
        parent_cls: type[Any],
        key: str,
        config: dict,
    ) -> Any:
        cls_name = config.get("class")
        if cls_name is None:
            raise SourceProviderError(
                f"missing key 'class' in config {config}",
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
        base_cls: type[Any],
        cls_name: str,
    ) -> Optional[type[Any]]:
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

    def _instantiate_class(self, cls: type[T], config: dict[str, Any]) -> T:
        kwargs = {
            k: self._convert_arg(cls, k, v) for k, v in config.items() if k != "class"
        }

        return cls(**kwargs)

    def _convert_arg(self, parent_cls: type[Any], key: str, arg: Any) -> Any:
        if isinstance(arg, dict):
            if "class" in arg:
                return self._create_object(parent_cls, key, arg)

            return {k: self._convert_arg(parent_cls, k, v) for k, v in arg.items()}

        if isinstance(arg, list):
            return [self._convert_arg(parent_cls, key, v) for v in arg]

        if isinstance(arg, str) and arg.startswith("$"):
            if arg.startswith("$$"):
                return arg[1:]

            return ContextValue(arg)

        return arg

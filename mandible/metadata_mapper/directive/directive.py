from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, Type

from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.key import Key
from mandible.metadata_mapper.source import Source
from mandible.metadata_mapper.types import Key as KeyType

DIRECTIVE_REGISTRY: Dict[str, Type["TemplateDirective"]] = {}


def get_key(key: KeyType, context: Context, key_options: dict) -> Key:
    if callable(key):
        key = key(context)

    return Key(key, **key_options)


@dataclass
class TemplateDirective(ABC):
    """Base class for directives in a metadata template.

    A directive is a special marker in the metadata template which will be
    replaced by the MetadataMapper.
    """
    # Registry boilerplate
    def __init_subclass__(
        cls,
        register: bool = True,
        name: Optional[str] = None,
        **kwargs,
    ):
        if register:
            name = name or cls.__name__.lower()
            DIRECTIVE_REGISTRY[name] = cls
            cls.directive_name = name

        super().__init_subclass__(**kwargs)

    # Begin class definition
    directive_name: ClassVar[Optional[str]] = None

    context: Context
    sources: Dict[str, Source]

    @abstractmethod
    def call(self):
        pass

    def prepare(self):
        pass

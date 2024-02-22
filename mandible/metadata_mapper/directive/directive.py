from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar, Dict, Optional, Type

from ..context import Context
from ..source import Source
from ..types import Key

DIRECTIVE_REGISTRY: Dict[str, Type["TemplateDirective"]] = {}


def get_key(key: Key, context: Context) -> str:
    if callable(key):
        key = key(context)

    return key


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

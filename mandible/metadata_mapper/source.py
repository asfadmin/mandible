import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from .context import Context
from .format import Format
from .key import Key
from .storage import Storage

log = logging.getLogger(__name__)


SOURCE_REGISTRY: dict[str, type["Source"]] = {}


@dataclass
class Source(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True, **kwargs):
        if register:
            SOURCE_REGISTRY[cls.__name__] = cls

        super().__init_subclass__(**kwargs)

    # Begin class definition
    def __post_init__(self):
        self._keys: set[Key] = set()
        self._values: dict[Key, Any] = {}

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
                new_values,
            )
            self._values.update(new_values)

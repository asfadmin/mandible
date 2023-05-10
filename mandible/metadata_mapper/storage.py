import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import IO, Any, Dict, Type

import s3fs

from .context import Context


class StorageError(Exception):
    pass


STORAGE_REGISTRY: Dict[str, Type["Storage"]] = {}


@dataclass
class Storage(ABC):
    # Registry boilerplate
    def __init_subclass__(cls):
        STORAGE_REGISTRY[cls.__name__] = cls

    # Begin class definition
    filters: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self._compiled_filters = {
            k: re.compile(v) if isinstance(v, str) else v
            for k, v in self.filters.items()
        }

    def open_file(self, context: Context) -> IO[bytes]:
        file = self.get_file_from_context(context)
        return self._open_file(file)

    def get_file_from_context(self, context: Context) -> Dict[str, Any]:
        """Return the file from the context which matches all filters."""

        # Special error message to make debugging empty context easier
        if not context.files:
            raise StorageError("no files in context")

        for info in context.files:
            if self._matches_filters(info):
                return info

        raise StorageError(f"no files matched filters {self.filters}")

    def _matches_filters(self, info: Dict[str, Any]) -> bool:
        for key, pattern in self._compiled_filters.items():
            if key not in info:
                return False

            value = info[key]
            if isinstance(pattern, re.Pattern):
                if not pattern.fullmatch(value):
                    return False
            elif value != pattern:
                return False

        return True

    @abstractmethod
    def _open_file(self, info: Dict) -> IO[bytes]:
        pass


class LocalFile(Storage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        return open(info["path"], "rb")


class S3File(Storage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False)
        return s3.open(f"s3://{info['bucket']}/{info['key']}")

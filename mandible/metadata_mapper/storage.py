import io
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import IO, Any, Dict, Type, Union

import s3fs

from .context import Context


class StorageError(Exception):
    pass


STORAGE_REGISTRY: Dict[str, Type["Storage"]] = {}


class Storage(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True):
        if register:
            STORAGE_REGISTRY[cls.__name__] = cls

    @abstractmethod
    def open_file(self, context: Context) -> IO[bytes]:
        """Get a filelike object to access the data."""
        pass


@dataclass
class Dummy(Storage):
    """A dummy storage that returns a hardcoded byte stream.

    Used for testing.
    """

    data: Union[str, bytes]

    def open_file(self, context: Context) -> IO[bytes]:
        if isinstance(self.data, str):
            data = self.data.encode()
        else:
            data = self.data

        return io.BytesIO(data)


@dataclass
class FilteredStorage(Storage, register=False):
    """A storage which matches a set of filters on the context's files and
    returns data from the matching file.
    """
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


@dataclass
class LocalFile(FilteredStorage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        return open(info["path"], "rb")


@dataclass
class S3File(FilteredStorage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False)
        return s3.open(f"s3://{info['bucket']}/{info['key']}")

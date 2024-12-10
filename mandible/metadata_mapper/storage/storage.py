import io
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import IO, Any, Optional, Union

import s3fs

from mandible.metadata_mapper.context import Context


class StorageError(Exception):
    pass


STORAGE_REGISTRY: dict[str, type["Storage"]] = {}


class Storage(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True, **kwargs):
        if register:
            STORAGE_REGISTRY[cls.__name__] = cls

        super().__init_subclass__(**kwargs)

    # Begin class definition
    @abstractmethod
    def open_file(self, context: Context) -> IO[bytes]:
        """Get a filelike object to access the data."""
        pass


# Define placeholders for when extras are not installed


@dataclass
class _PlaceholderBase(Storage, register=False):
    """
    Base class for defining placeholder implementations for classes that
    require extra dependencies to be installed
    """
    def __init__(self, dep: str):
        raise Exception(
            f"{dep} must be installed to use the {self.__class__.__name__} "
            "format class"
        )

    def open_file(self, context: Context) -> IO[bytes]:
        pass


@dataclass
class HttpRequest(_PlaceholderBase):
    def __init__(self):
        super().__init__("requests")


@dataclass
class CmrQuery(_PlaceholderBase):
    def __init__(self):
        super().__init__("requests")


# Define storages that don't require extra dependencies

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
    filters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self._compiled_filters_cache: Optional[dict[str, Any]] = None

    @property
    def _compiled_filters(self) -> dict[str, Any]:
        if self._compiled_filters_cache is None:
            self._compiled_filters_cache = {
                k: re.compile(v) if isinstance(v, str) else v
                for k, v in self.filters.items()
            }

        return self._compiled_filters_cache

    def open_file(self, context: Context) -> IO[bytes]:
        file = self.get_file_from_context(context)
        return self._open_file(file)

    def get_file_from_context(self, context: Context) -> dict[str, Any]:
        """Return the file from the context which matches all filters."""

        # Special error message to make debugging empty context easier
        if not context.files:
            raise StorageError("no files in context")

        for info in context.files:
            if self._matches_filters(info):
                return info

        raise StorageError(f"no files matched filters {self.filters}")

    def _matches_filters(self, info: dict[str, Any]) -> bool:
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
    def _open_file(self, info: dict) -> IO[bytes]:
        pass


@dataclass
class LocalFile(FilteredStorage):
    """A storage which reads from the file system"""

    def _open_file(self, info: dict) -> IO[bytes]:
        return open(info["path"], "rb")


@dataclass
class S3File(FilteredStorage):
    """A storage which reads from an AWS S3 object"""

    s3fs_kwargs: dict[str, Any] = field(default_factory=dict)

    def _open_file(self, info: dict) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False, **self.s3fs_kwargs)
        return s3.open(f"s3://{info['bucket']}/{info['key']}")

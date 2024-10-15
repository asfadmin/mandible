import contextlib
import json
import re
import zipfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, Any, ContextManager, Dict, Iterable, Type, TypeVar

from mandible import jsonpath
from mandible.metadata_mapper.key import RAISE_EXCEPTION, Key

T = TypeVar("T")


class FormatError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason


FORMAT_REGISTRY: Dict[str, Type["Format"]] = {}


@dataclass
class Format(ABC):
    # Registry boilerplate
    def __init_subclass__(cls, register: bool = True, **kwargs):
        if register:
            FORMAT_REGISTRY[cls.__name__] = cls

        super().__init_subclass__(**kwargs)

    # Begin class definition
    @abstractmethod
    def get_values(
        self,
        file: IO[bytes],
        keys: Iterable[Key],
    ) -> Dict[Key, Any]:
        """Get a list of values from a file"""
        pass

    @abstractmethod
    def get_value(self, file: IO[bytes], key: Key) -> Any:
        """Convenience function for getting a single value"""
        pass


@dataclass
class FileFormat(Format, ABC, register=False):
    """A Format for querying files from a standard data file.

    Simple, single format data types such as 'json' that can be queried
    directly.
    """

    def get_values(
        self,
        file: IO[bytes],
        keys: Iterable[Key],
    ) -> Dict[Key, Any]:
        """Get a list of values from a file"""

        with self.parse_data(file) as data:
            return {
                key: self._eval_key_wrapper(data, key)
                for key in keys
            }

    def get_value(self, file: IO[bytes], key: Key) -> Any:
        """Convenience function for getting a single value"""

        with self.parse_data(file) as data:
            return self._eval_key_wrapper(data, key)

    def _eval_key_wrapper(self, data, key: Key) -> Any:
        try:
            return self.eval_key(data, key)
        except KeyError as e:
            if key.default is not RAISE_EXCEPTION:
                return key.default
            raise FormatError(f"key not found {repr(key.key)}") from e
        except Exception as e:
            raise FormatError(f"{repr(key.key)} {e}") from e

    @staticmethod
    @abstractmethod
    def parse_data(file: IO[bytes]) -> ContextManager[T]:
        """Parse the binary stream into a queryable data structure.

        The return type can be anything, but must be compatible with the input
        to `eval_key`.

        :param file: The binary stream to parse
        :returns: A queryable data structure that will be passed to `eval_key`
        """
        pass

    @staticmethod
    @abstractmethod
    def eval_key(data: T, key: Key) -> Any:
        """Query the parsed data for a key.

        :param data: Object returned by `parse_data`
        :param key: The key to extract
        :returns: The value associated with the key
        :raises: KeyError
        """
        pass


# Define placeholders for when extras are not installed


@dataclass
class _PlaceholderBase(FileFormat, register=False):
    """
    Base class for defining placeholder implementations for classes that
    require extra dependencies to be installed
    """
    def __init__(self, dep: str):
        raise Exception(
            f"{dep} must be installed to use the {self.__class__.__name__} "
            "format class"
        )

    @staticmethod
    def parse_data(file: IO[bytes]) -> ContextManager[T]:
        pass

    @staticmethod
    def eval_key(data: T, key: Key):
        pass


@dataclass
class H5(_PlaceholderBase):
    def __init__(self):
        super().__init__("h5py")


@dataclass
class Xml(_PlaceholderBase):
    def __init__(self):
        super().__init__("lxml")


# Define formats that don't require extra dependencies

@dataclass
class Json(FileFormat):
    @staticmethod
    @contextlib.contextmanager
    def parse_data(file: IO[bytes]) -> dict:
        yield json.load(file)

    @staticmethod
    def eval_key(data: dict, key: Key):
        values = jsonpath.get(data, key.key)

        return key.resolve_list_match(values)


@dataclass
class ZipMember(Format):
    """A member from a zip archive.

    :param filters: A set of filters used to select the desired archive member
    :param format: The Format of the archive member
    """

    filters: Dict[str, Any]
    """Filter against any attributes of zipfile.ZipInfo objects"""
    format: Format

    def __post_init__(self):
        self._compiled_filters = {
            k: re.compile(v) if isinstance(v, str) else v
            for k, v in self.filters.items()
        }

    def get_values(
        self,
        file: IO[bytes],
        keys: Iterable[Key],
    ) -> Dict[Key, Any]:
        """Get a list of values from a file"""

        with zipfile.ZipFile(file, "r") as zf:
            file = self._get_file_from_archive(zf)
            return self.format.get_values(file, keys)

    def get_value(self, file: IO[bytes], key: Key) -> Any:
        """Convenience function for getting a single value"""

        with zipfile.ZipFile(file, "r") as zf:
            file = self._get_file_from_archive(zf)
            return self.format.get_value(file, key)

    def _get_file_from_archive(self, zf: zipfile.ZipFile) -> IO[bytes]:
        """Return the member from the archive which matches all filters."""

        zipinfo_list = zf.infolist()

        # Special error message to make debugging empty archive easier
        if not zipinfo_list:
            raise FormatError("no members in archive")

        for zipinfo in zipinfo_list:
            if self._matches_filters(zipinfo):
                return zf.open(zipinfo, "r")

        raise FormatError(f"no archive members matched filters {self.filters}")

    def _matches_filters(self, zipinfo: zipfile.ZipInfo) -> bool:
        for key, pattern in self._compiled_filters.items():
            try:
                value = getattr(zipinfo, key)
            except AttributeError:
                return False

            # The is_dir method can't be accessed because we don't include a
            # mechanism for calling it. We could add a special case, or a
            # feature to call member functions automatically, but as there is
            # no use case for matching a directory inside the archive, we just
            # leave it unimplemented.

            if isinstance(pattern, re.Pattern):
                if not pattern.fullmatch(value):
                    return False
            elif value != pattern:
                return False

        return True


@dataclass
class ZipInfo(FileFormat):
    """Query Zip headers and directory information."""

    @staticmethod
    @contextlib.contextmanager
    def parse_data(file: IO[bytes]) -> dict:
        with zipfile.ZipFile(file, "r") as zf:
            yield {
                "infolist": [
                    {
                        k: getattr(info, k)
                        for k in info.__slots__
                        if not k.startswith("_")
                    }
                    for info in zf.infolist()
                ],
                "filename": zf.filename,
                "comment": zf.comment,
            }

    @staticmethod
    def eval_key(data: dict, key: Key) -> Any:
        values = jsonpath.get(data, key.key)

        return key.resolve_list_match(values)

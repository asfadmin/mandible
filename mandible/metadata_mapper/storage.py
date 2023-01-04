import re
from abc import ABC, abstractmethod
from typing import IO, Dict, Type, Union

import s3fs


class Storage(ABC):
    _SUBCLASSES: Dict[str, "Storage"] = {}

    def __init_subclass__(cls):
        Storage._SUBCLASSES[cls.__name__] = cls

    @classmethod
    def get_subclass(cls, name: str) -> "Storage":
        return cls._SUBCLASSES[name]

    def __init__(
        self,
        *,
        name: str = None,
        name_match: Union[str, re.Pattern] = None
    ):
        if name is None and name_match is None:
            raise ValueError(
                "You must provide either a 'name' xor 'name_match' argument"
            )
        if name is not None and name_match is not None:
            raise ValueError(
                "You can't provide both a 'name' and 'name_match' argument"
            )
        self.name = name
        self.name_match = name_match

    def open_file(self, context: "Context") -> IO[bytes]:
        if self.name is not None:
            file = context.files[self.name]
        elif self.name_match is not None:
            if not isinstance(self.name_match, re.Pattern):
                self.name_match = re.compile(self.name_match)

            for file_name, file_info in context.files.items():
                if self.name_match.match(file_name):
                    file = file_info
                    break
            else:
                raise RuntimeError(
                    f"No files matched pattern '{self.name_match.pattern}'"
                )

        return self._open_file(file)

    @abstractmethod
    def _open_file(self, info: Dict) -> IO[bytes]:
        pass


class LocalFile(Storage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        return open(info["path"], "rb")


class S3File(Storage):
    def _open_file(self, info: Dict) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False)
        return s3.open(info["s3uri"])

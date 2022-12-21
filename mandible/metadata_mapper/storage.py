from abc import ABC, abstractmethod
from typing import IO, Dict

import s3fs


class Storage(ABC):
    _SUBCLASSES: Dict[str, "Storage"] = {}

    def __init_subclass__(cls):
        Storage._SUBCLASSES[cls.__name__] = cls

    @classmethod
    def get_subclass(cls, name: str) -> "Storage":
        return cls._SUBCLASSES[name]

    @abstractmethod
    def get_file(self) -> IO[bytes]:
        pass


class LocalFile(Storage):
    def __init__(self, path: str, **kwargs):
        self.path = path

    def get_file(self) -> IO[bytes]:
        return open(self.path, "rb")


class S3File(Storage):
    def __init__(self, s3uri: str, **kwargs):
        self.s3uri = s3uri

    def get_file(self) -> IO[bytes]:
        s3 = s3fs.S3FileSystem(anon=False)
        return s3.open(self.s3uri)

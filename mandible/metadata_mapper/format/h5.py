from dataclasses import dataclass
from typing import IO, Any, ContextManager

import h5py

from mandible.h5_parser import normalize

from .format import SimpleFormat


@dataclass
class H5(SimpleFormat):
    @staticmethod
    def _parse_data(file: IO[bytes]) -> ContextManager[Any]:
        return h5py.File(file, "r")

    @staticmethod
    def _eval_key(data, key: str):
        return normalize(data[key][()])

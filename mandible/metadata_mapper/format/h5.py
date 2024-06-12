from dataclasses import dataclass
from typing import IO, Any, ContextManager

import h5py

from mandible.h5_parser import normalize

from .format import Format


@dataclass
class H5(Format):
    @staticmethod
    def _parse_data(file: IO[bytes]) -> ContextManager[Any]:
        return h5py.File(file, "r")

    @staticmethod
    def _eval_key(data, key: str):
        return normalize(data[key][()])

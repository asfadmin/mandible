import contextlib
from dataclasses import dataclass
from typing import IO, Any

import h5py
import numpy as np

from mandible.metadata_mapper.key import Key

from .format import FileFormat


@dataclass
class H5(FileFormat[Any]):
    @staticmethod
    def parse_data(file: IO[bytes]) -> contextlib.AbstractContextManager[Any]:
        return h5py.File(file, "r")

    @staticmethod
    def eval_key(data: Any, key: Key) -> Any:
        return normalize(data[key.key][()])


def normalize(node_val: Any) -> Any:
    if isinstance(node_val, np.bool_):
        return bool(node_val)
    if isinstance(node_val, np.integer):
        return int(node_val)
    if isinstance(node_val, np.floating):
        return float(node_val)
    if isinstance(node_val, np.ndarray):
        value = node_val.tolist()
        if isinstance(value[0], bytes):
            value = [x.decode("utf-8") for x in value]
        return value
    if isinstance(node_val, bytes):
        return node_val.decode("utf-8")

    return node_val

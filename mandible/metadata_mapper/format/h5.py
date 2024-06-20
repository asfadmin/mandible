from dataclasses import dataclass
from typing import IO, Any, ContextManager

import h5py
import numpy as np


from .format import SimpleFormat


@dataclass
class H5(SimpleFormat):
    @staticmethod
    def _parse_data(file: IO[bytes]) -> ContextManager[Any]:
        return h5py.File(file, "r")

    @staticmethod
    def _eval_key(data, key: str):
        return normalize(data[key][()])


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

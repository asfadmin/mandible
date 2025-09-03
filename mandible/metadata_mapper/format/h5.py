import contextlib
from dataclasses import dataclass
from typing import IO, Any, Optional

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
        group_key, attribute_key = parse_key(key.key)
        if attribute_key is not None:
            return normalize(data[group_key].attrs.get(attribute_key))
        return normalize(data[group_key][()])


def parse_key(key: str) -> tuple[str, Optional[str]]:
    """Parse a HDF5 key where '@' separates the group name from an attribute name.

    The special @ character can be escaped as @@ if the group or attribute name contains a literal '@'.
    :returns: (str, str | None) -- the group name and the attribute name (if any)
    """

    # HDF5 states null character is not a valid group name
    # https://docs.hdfgroup.org/documentation/hdf5/latest/_l_b_grp_create_names.html
    placeholder = "\0"
    temp = key.replace("@@", placeholder)

    if temp.count("@") > 1:
        raise ValueError(f"Invalid key: multiple '@' in '{key}'")

    if "@" not in temp:
        return temp.replace(placeholder, "@"), None

    left, right = temp.split("@", 1)

    return left.replace(placeholder, "@"), right.replace(placeholder, "@")


def normalize(node_val: Any) -> Any:
    if isinstance(node_val, np.bool_):
        return bool(node_val)
    if isinstance(node_val, np.integer):
        return int(node_val)
    if isinstance(node_val, np.floating):
        return float(node_val)
    if isinstance(node_val, np.ndarray):
        value = [
            # ruff hint
            x.decode("utf-8") if isinstance(x, bytes) else x
            for x in node_val.tolist()
        ]
        return value
    if isinstance(node_val, bytes):
        return node_val.decode("utf-8")

    return node_val

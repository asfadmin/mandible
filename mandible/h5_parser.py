import logging

import h5py
import numpy as np


class H5parser(dict):
    """
    Parser for *.h5 files
    Pre: A list of groups to be included,
    this must be very specific full path to the group
    Post: Dict with h5 groups md_name as keys
    """
    def __init__(self, h5_groups):
        self.h5_groups = h5_groups
        self.log = logging.getLogger(__name__)

    def read_file(self, file: str) -> None:
        with h5py.File(file, "r") as h5f:
            for key in self.h5_groups:
                try:
                    node_val = h5f[key][()]
                except KeyError:
                    raise KeyError(key)
                self[key] = normalize(node_val)


def normalize(node_val):
    if isinstance(node_val, np.ndarray):
        value = node_val.tolist()
        if isinstance(value[0], bytes):
            value = [x.decode("utf-8") for x in value]
        return value
    if isinstance(node_val, bytes):
        return node_val.decode("utf-8")

    return node_val

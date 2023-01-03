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
                node_val = h5f[key][()]
                if isinstance(node_val, np.integer):
                    node_val = int(node_val)
                if isinstance(node_val, np.floating):
                    node_val = float(node_val)
                if isinstance(node_val, np.ndarray):
                    node_val = node_val.tolist()
                    if isinstance(node_val[0], bytes):
                        node_val = [x.decode("utf-8") for x in node_val]
                if isinstance(node_val, bytes):
                    node_val = node_val.decode("utf-8")
                self[key] = node_val

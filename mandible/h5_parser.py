import h5py
import numpy as np


class H5parser(dict):
    """
    Parser for *.h5 files
    Pre: A list of groups to be included,
    this can be very specific full path or generic groups like 'metadata'
    Post: Dict with h5 groups as keys
    """
    def __init__(self, h5_groups):
        self.h5_groups = h5_groups

    def _get_h5_dict(self, _, node) -> None:
        fullname = node.name
        if not isinstance(node, h5py.Dataset):
            return None

        if not (
            any([True for group in self.h5_groups if group in fullname])
        ):
            return None

        key = fullname.split("/")[-1]
        node_val = node[()]
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

    def read_file(self, file: str) -> None:
        with h5py.File(file, "r") as h5f:
            h5f.visititems(self._get_h5_dict)

import h5py
import numpy as np
import pytest

from mandible.h5_parser import H5parser


@pytest.fixture
def h5_test_file(tmp_path):
    filename = tmp_path / "test.h5"
    dataset_1 = np.array((0.0, 0.1, 0.2, 0.3, 0.4, 0.5))
    dataset_2 = np.array((b"Testing"))
    with h5py.File(filename, "w") as hf:
        group_1 = hf.create_group("test")
        group_2 = hf.create_group("test/long/path/metadata")
        group_1.create_dataset("tester", data=dataset_1)
        group_2.create_dataset("test_meta", data=dataset_2)
    yield filename
    filename.unlink()


def test_h5_parser_parent_key(h5_test_file):
    groups = ["test/long/path/metadata/test_meta", "/test/tester"]
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {
        "test/long/path/metadata/test_meta": "Testing",
        "/test/tester": [
            0.0,
            0.1,
            0.2,
            0.3,
            0.4,
            0.5
        ]
    }


def test_h5_parser_single_key(h5_test_file):
    groups = ["test/long/path/metadata/test_meta"]
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {
        "test/long/path/metadata/test_meta": "Testing"
    }


def test_h5_parser_no_group(h5_test_file):
    groups = []
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {}


def test_h5_praser_group_missing(h5_test_file):
    groups = ["test/long/path/metadata/test_meta", "thing", "here"]
    with pytest.raises(KeyError, match="thing"):
        data = H5parser(groups)
        data.read_file(h5_test_file)

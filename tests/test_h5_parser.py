import json

import pytest

try:
    import h5py
    import numpy as np

    from mandible.h5_parser import H5parser
except ImportError:
    pass

pytestmark = pytest.mark.h5


@pytest.fixture
def h5_test_file(tmp_path):
    filename = tmp_path / "test.h5"
    dataset_1 = np.array((0.0, 0.1, 0.2, 0.3, 0.4, 0.5))
    dataset_2 = np.array((b"Testing"))
    with h5py.File(filename, "w") as hf:
        group_1 = hf.create_group("test")
        group_2 = hf.create_group("test/long/path/metadata")
        group_types = hf.create_group("types")
        group_1.create_dataset("float_array", data=dataset_1)
        group_2.create_dataset("string", data=dataset_2)

        group_types.create_dataset("string", data="Hello World")
        group_types.create_dataset("integer", data=10)
        group_types.create_dataset("unsigned_integer", dtype=np.uint, data=20)
        group_types.create_dataset("float", data=10.5)
        group_types.create_dataset("float16", dtype=np.float16, data=20.5)
        group_types.create_dataset("boolean", data=True)
    yield filename
    filename.unlink()


def test_h5_parser_parent_key(h5_test_file):
    groups = ["test/long/path/metadata/string", "/test/float_array"]
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {
        "test/long/path/metadata/string": "Testing",
        "/test/float_array": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    }


def test_h5_parser_single_key(h5_test_file):
    groups = ["test/long/path/metadata/string"]
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {"test/long/path/metadata/string": "Testing"}


def test_h5_parser_no_group(h5_test_file):
    groups = []
    data = H5parser(groups)
    data.read_file(h5_test_file)
    assert data == {}


def test_h5_praser_group_missing(h5_test_file):
    groups = ["test/long/path/metadata/string", "thing", "here"]
    with pytest.raises(KeyError, match="thing"):
        data = H5parser(groups)
        data.read_file(h5_test_file)


def test_h5_parser_types(h5_test_file):
    expected = {
        "types/string": "Hello World",
        "types/integer": 10,
        "types/unsigned_integer": 20,
        "types/float": 10.5,
        "types/float16": 20.5,
        "types/boolean": True,
    }
    groups = list(expected)
    data = H5parser(groups)
    data.read_file(h5_test_file)

    assert data == expected
    # Check that types are JSON serializable
    assert json.loads(json.dumps(data)) == expected

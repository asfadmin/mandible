import pytest

pytestmark = pytest.mark.h5


def test_normalize():
    # Importing inside of the test since the imports might fail if h5py is not
    # installed. Pytest will ensure the tests are not run in that case by using
    # the pytest mark.
    import numpy as np

    from mandible.metadata_mapper.format.h5 import normalize

    assert normalize(np.bool_(True)) is True
    assert normalize(np.bool_(False)) is False
    assert normalize(np.int64(10)) == 10
    assert normalize(np.float64(123.45)) == 123.45
    assert normalize(np.str_("foo")) == "foo"
    assert normalize(np.bytes_(b"foo")) == "foo"
    assert normalize(np.array([True, False], dtype=np.bool_)) == [True, False]
    assert normalize(np.array([1, 2], dtype=np.int64)) == [1, 2]
    assert normalize(np.array([1.2, 2.3], dtype=np.float64)) == [1.2, 2.3]
    assert normalize(np.array(["A", "B"], dtype="|S1")) == ["A", "B"]
    assert normalize(np.array(["A", "B"], dtype="O")) == ["A", "B"]
    assert normalize(np.array([], dtype="|S1")) == []

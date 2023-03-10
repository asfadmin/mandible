import io
from unittest import mock

import pytest

from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.format import Format
from mandible.metadata_mapper.source import Source
from mandible.metadata_mapper.storage import Storage


@pytest.fixture
def mock_context():
    return mock.create_autospec(Context)


@pytest.fixture
def mock_format():
    return mock.create_autospec(Format)


@pytest.fixture
def mock_storage():
    return mock.create_autospec(Storage)


def test_source(mock_context, mock_format, mock_storage):
    mock_storage.open_file.return_value = io.BytesIO(b"mock data")
    mock_format.get_values.return_value = {
        "foo": "foo value",
        "bar": "bar value"
    }

    source = Source(
        mock_storage,
        mock_format
    )

    source.add_key("foo")
    source.add_key("bar")

    with pytest.raises(KeyError):
        source.get_value("foo")

    source.query_all_values(mock_context)

    assert source.get_value("foo") == "foo value"
    assert source.get_value("bar") == "bar value"


def test_source_query_no_keys(mock_context, mock_format, mock_storage):
    source = Source(
        mock_storage,
        mock_format
    )

    source.query_all_values(mock_context)

    mock_storage.open_file.assert_not_called()
    mock_format.get_values.assert_not_called()

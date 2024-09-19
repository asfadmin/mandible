import io
from dataclasses import dataclass
from unittest import mock

import pytest

from mandible.metadata_mapper import FileSource, Format
from mandible.metadata_mapper.context import Context
from mandible.metadata_mapper.key import Key
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
        Key("foo"): "foo value",
        Key("bar"): "bar value",
    }

    source = FileSource(
        mock_storage,
        mock_format,
    )

    source.add_key(Key("foo"))
    source.add_key(Key("bar"))

    with pytest.raises(KeyError):
        source.get_value(Key("foo"))

    source.query_all_values(mock_context)

    assert source.get_value(Key("foo")) == "foo value"
    assert source.get_value(Key("bar")) == "bar value"


def test_source_query_no_keys(mock_context, mock_format, mock_storage):
    source = FileSource(
        mock_storage,
        mock_format,
    )

    source.query_all_values(mock_context)

    mock_storage.open_file.assert_not_called()
    mock_format.get_values.assert_not_called()


def test_custom_source(mock_context):
    @dataclass
    class CustomSource(Source):
        arg1: str

        def query_all_values(self, context: Context):
            self._values.update({
                key: key.key
                for key in self._keys
            })

    source = CustomSource("foo")
    source.add_key(Key("hello"))

    source.query_all_values(mock_context)

    assert source._values == {
        Key("hello"): "hello",
    }

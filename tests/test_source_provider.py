import pytest

from mandible.metadata_mapper.format import Json, Xml
from mandible.metadata_mapper.source import (
    ConfigSourceProvider,
    PySourceProvider,
    Source,
)
from mandible.metadata_mapper.storage import LocalFile


@pytest.fixture
def sources():
    return {
        "json": Source(LocalFile(filters={"name": "foo"}), Json()),
        "xml": Source(LocalFile(filters={"name": "foo"}), Xml())
    }


def test_py_source_provider(sources):
    provider = PySourceProvider(sources)

    assert provider.get_sources() == sources


def test_config_source_provider(sources):
    provider = ConfigSourceProvider({
        "json": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "foo"
                }
            },
            "format": {
                "class": "Json"
            }
        },
        "xml": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "foo"
                }
            },
            "format": {
                "class": "Xml"
            }
        }
    })

    assert provider.get_sources() == sources

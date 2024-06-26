import pytest

from mandible.metadata_mapper.format import FORMAT_REGISTRY, H5, Json, Xml, Zip
from mandible.metadata_mapper.source import (
    ConfigSourceProvider,
    PySourceProvider,
    Source,
    SourceProviderError,
)
from mandible.metadata_mapper.storage import STORAGE_REGISTRY, LocalFile


@pytest.fixture
def sources():
    return {
        "foo": Source(LocalFile(filters={"name": "foo"}), Json()),
        "bar": Source(LocalFile(filters={"name": "bar"}), Json()),
        "baz": Source(
            LocalFile(filters={"name": "baz"}),
            Zip(
                filters={
                    "filename": "foo",
                },
                format=Json(),
            ),
        ),
    }


def test_py_source_provider(sources):
    provider = PySourceProvider(sources)

    assert provider.get_sources() == sources


def test_config_source_provider(sources):
    provider = ConfigSourceProvider({
        "foo": {
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
        "bar": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "bar"
                }
            },
            "format": {
                "class": "Json"
            }
        },
        "baz": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "baz",
                },
            },
            "format": {
                "class": "Zip",
                "filters": {
                    "filename": "foo",
                },
                "format": {
                    "class": "Json",
                },
            },
        },
    })

    assert provider.get_sources() == sources


@pytest.mark.h5
@pytest.mark.xml
def test_config_source_provider_all_formats():
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
                    "name": "bar"
                }
            },
            "format": {
                "class": "Xml"
            }
        },
        "h5": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "baz"
                }
            },
            "format": {
                "class": "H5"
            }
        }
    })

    assert provider.get_sources() == {
        "json": Source(LocalFile(filters={"name": "foo"}), Json()),
        "xml": Source(LocalFile(filters={"name": "bar"}), Xml()),
        "h5": Source(LocalFile(filters={"name": "baz"}), H5())
    }


def test_config_source_provider_empty():
    provider = ConfigSourceProvider({})

    assert provider.get_sources() == {}


def test_config_source_provider_missing_storage():
    provider = ConfigSourceProvider({
        "source": {
            "format": {
                "class": "Json"
            }
        }
    })

    with pytest.raises(
        SourceProviderError,
        match="failed to create source 'source': missing key 'storage'"
    ):
        provider.get_sources()


def test_config_source_provider_invalid_storage():
    provider = ConfigSourceProvider({
        "source": {
            "storage": {
                "class": "NotARealStorage"
            }
        }
    })

    with pytest.raises(
        SourceProviderError,
        match=(
            "failed to create source 'source': "
            "invalid storage type 'NotARealStorage'"
        )
    ):
        provider.get_sources()


@pytest.mark.parametrize("cls_name", STORAGE_REGISTRY.keys())
def test_config_source_provider_invalid_storage_kwargs(cls_name):
    provider = ConfigSourceProvider({
        "source": {
            "storage": {
                "class": cls_name,
                "invalid_arg": 1
            }
        }
    })

    with pytest.raises(
        SourceProviderError,
        match=(
            "failed to create source 'source': "
            rf"({cls_name}\.)?__init__\(\) got an unexpected keyword argument "
            "'invalid_arg'"
        )
    ):
        provider.get_sources()


def test_config_source_provider_missing_format():
    provider = ConfigSourceProvider({
        "source": {
            "storage": {
                "class": "S3File"
            }
        }
    })

    with pytest.raises(
        SourceProviderError,
        match="failed to create source 'source': missing key 'format'"
    ):
        provider.get_sources()


def test_config_source_provider_invalid_format():
    provider = ConfigSourceProvider({
        "source": {
            "storage": {
                "class": "S3File"
            },
            "format": {
                "class": "NotARealFormat"
            }
        }
    })

    with pytest.raises(
        SourceProviderError,
        match=(
            "failed to create source 'source': "
            "invalid format type 'NotARealFormat'"
        )
    ):
        provider.get_sources()


@pytest.mark.parametrize("cls_name", FORMAT_REGISTRY.keys())
def test_config_source_provider_invalid_format_kwargs(cls_name):
    provider = ConfigSourceProvider({
        "source": {
            "storage": {
                "class": "S3File"
            },
            "format": {
                "class": cls_name,
                "invalid_arg": 1,
            },
        },
    })

    with pytest.raises(
        SourceProviderError,
        match=(
            "failed to create source 'source': "
            rf"({cls_name}\.)?__init__\(\) got an unexpected keyword argument "
            "'invalid_arg'"
        )
    ):
        provider.get_sources()

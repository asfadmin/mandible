from dataclasses import dataclass

import pytest

from mandible.metadata_mapper import Context, FileSource
from mandible.metadata_mapper.context import ContextValue
from mandible.metadata_mapper.format import FORMAT_REGISTRY, H5, Json, Xml, ZipMember
from mandible.metadata_mapper.source import Source
from mandible.metadata_mapper.source_provider import (
    ConfigSourceProvider,
    PySourceProvider,
    SourceProviderError,
)
from mandible.metadata_mapper.storage import (
    STORAGE_REGISTRY,
    FilteredStorage,
    LocalFile,
)


@dataclass
class DummySource(Source):
    arg1: str
    storage: FilteredStorage

    def query_all_values(self, context: Context):
        pass


@pytest.fixture
def sources():
    return {
        "foo": FileSource(LocalFile(filters={"name": "foo"}), Json()),
        "bar": FileSource(LocalFile(filters={"name": "bar"}), Json()),
        "baz": FileSource(
            LocalFile(filters={"name": "baz"}),
            ZipMember(
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
                "class": "ZipMember",
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


def test_config_source_provider_source_type():
    provider = ConfigSourceProvider({
        "foo": {
            "class": "DummySource",
            "arg1": "foobar",
            "storage": {
                "class": "LocalFile",
            },
        },
    })

    assert provider.get_sources() == {
        "foo": DummySource(
            arg1="foobar",
            storage=LocalFile(),
        ),
    }


def test_config_source_provider_wrong_base_class_type():
    provider = ConfigSourceProvider({
        "foo": {
            "class": "DummySource",
            "arg1": "foobar",
            "storage": {
                # Dummy storage is not a FilteredStorage
                "class": "Dummy",
            },
        },
    })

    with pytest.raises(
        SourceProviderError,
        match=(
            "failed to create source 'foo': invalid storage type 'Dummy' must "
            "be a subclass of 'FilteredStorage'"
        ),
    ):
        provider.get_sources()


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
        "json": FileSource(LocalFile(filters={"name": "foo"}), Json()),
        "xml": FileSource(LocalFile(filters={"name": "bar"}), Xml()),
        "h5": FileSource(LocalFile(filters={"name": "baz"}), H5()),
    }


def test_config_source_provider_empty():
    provider = ConfigSourceProvider({})

    assert provider.get_sources() == {}


def test_config_source_provider_context_values():
    provider = ConfigSourceProvider({
        "arg": {
            "storage": {
                "class": "LocalFile",
                "filters": "$.meta.filters",
            },
            "format": {
                "class": "Json",
            },
        },
        "arg_nested": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "$.meta.name_filter",
                    "dollar": "$$.meta.not-replaced",
                },
            },
            "format": {
                "class": "Json",
            },
        },
    })

    assert provider.get_sources() == {
        "arg": FileSource(
            LocalFile(
                filters=ContextValue("$.meta.filters"),
            ),
            Json(),
        ),
        "arg_nested": FileSource(
            LocalFile(
                filters={
                    "name": ContextValue("$.meta.name_filter"),
                    "dollar": "$.meta.not-replaced",
                },
            ),
            Json(),
        ),
    }


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
        match=(
            r"failed to create source 'source': (FileSource\.)?__init__\(\) "
            "missing 1 required positional argument: 'storage'"
        ),
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
        match=(
            r"failed to create source 'source': (FileSource\.)?__init__\(\) "
            "missing 1 required positional argument: 'format'"
        ),
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

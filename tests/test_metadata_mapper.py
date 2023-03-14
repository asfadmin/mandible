import re

import pytest

from mandible.metadata_mapper import (
    ConfigSourceProvider,
    Context,
    MetadataMapper,
    MetadataMapperError,
    PySourceProvider,
    Source,
)
from mandible.metadata_mapper.format import Json, Xml
from mandible.metadata_mapper.storage import LocalFile


@pytest.fixture
def config():
    return {
        "sources": {
            "fixed_name_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": r"fixed_name_file\.json"
                    }
                },
                "format": {
                    "class": "Json",
                }
            },
            "name_match_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": r".*match_me\.json"
                    }
                },
                "format": {
                    "class": "Json"
                }
            },
            "fixed_xml_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "fixed_xml_file.xml"
                    }
                },
                "format": {
                    "class": "Xml"
                }
            },
        },
        "template": {
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "foo"
                }
            },
            "outer": {
                "nested": {
                    "@mapped": {
                        "source": "fixed_name_file",
                        "key": "nested.key"
                    }
                },
                "bar": {
                    "@mapped": {
                        "source": "name_match_file",
                        "key": "bar"
                    }
                }
            },
            "xml_foobar_1": {
                "@mapped": {
                    "source": "fixed_xml_file",
                    "key": "./foo/bar[1]/foobar"
                }
            },
            "xml_foobar_2": {
                "@mapped": {
                    "source": "fixed_xml_file",
                    "key": "./foo/bar[2]/foobar"
                }
            }
        }
    }


@pytest.fixture
def context(data_path):
    return Context(
        files=[
            {
                "name": "fixed_name_file.json",
                "path": str(data_path / "fixed_name_file.json")
            },
            {
                "name": "fixed_xml_file.xml",
                "path": str(data_path / "fixed_xml_file.xml")
            },
            {
                "name": "another_file.json"
            },
            {
                "name": "yet_another_file.json"
            },
            {
                "name": "first_match_me.json",
                "path": str(data_path / "match_me.json")
            },
            {
                "name": "dont_match_me.json"
            },
        ]
    )


@pytest.fixture
def mapper(config):
    return MetadataMapper(
        template=config["template"],
        source_provider=ConfigSourceProvider(config["sources"])
    )


def test_empty_mapping_empty_context():
    mapper = MetadataMapper({})
    assert mapper.get_metadata(Context()) == {}


def test_constant_mapping_empty_context():
    template = {
        "foo": "bar",
        "baz": "qux"
    }
    mapper = MetadataMapper(template)

    assert mapper.get_metadata(Context()) == template


def test_empty_context(mapper):
    context = Context()

    with pytest.raises(Exception, match="fixed_name_file"):
        mapper.get_metadata(context)


def test_basic(mapper, context):
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar"
        },
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_mapped_key_callable(config, context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "name_match_file",
                    "key": lambda ctx: ctx.meta["foo"]
                }
            },
        },
        source_provider=ConfigSourceProvider(config["sources"])
    )
    context.meta["foo"] = "bar"

    assert mapper.get_metadata(context) == {
        "foo": "value for bar"
    }


def test_basic_py_source_provider(config, context):
    mapper = MetadataMapper(
        template=config["template"],
        source_provider=PySourceProvider({
            "fixed_name_file": Source(
                storage=LocalFile(
                    filters={
                        "name": "fixed_name_file.json"
                    }
                ),
                format=Json()
            ),
            "fixed_xml_file": Source(
                storage=LocalFile(
                    filters={
                        "name": "fixed_xml_file.xml"
                    }
                ),
                format=Xml()
            ),
            "name_match_file": Source(
                storage=LocalFile(
                    filters={
                        "name": r".*match_me\.json"
                    }
                ),
                format=Json()
            ),
            "name_match_file2": Source(
                storage=LocalFile(
                    filters={
                        "name": re.compile(r".*match_me\.json")
                    }
                ),
                format=Json()
            )
        })
    )
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar"
        },
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_basic_s3_file(s3_resource, config, context):
    s3_resource.create_bucket(Bucket="test")
    s3_resource.Object("test", "fixed_name_file.json").put(
        Body=open(context.files[0]["path"]).read()
    )
    context.files[0]["s3uri"] = "s3://test/fixed_name_file.json"

    config["sources"]["fixed_name_file"]["storage"]["class"] = "S3File"

    mapper = MetadataMapper(
        template=config["template"],
        source_provider=ConfigSourceProvider(config["sources"])
    )

    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar"
        },
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_no_matching_files(config):
    mapper = MetadataMapper(
        template=config["template"],
        source_provider=ConfigSourceProvider(config["sources"])
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "no files matched filters"
        )
    ):
        mapper.get_metadata(Context())


def test_source_missing_key(config, context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "does not exist",
                }
            }
        },
        source_provider=ConfigSourceProvider(config["sources"])
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "key not found 'does not exist'"
        )
    ):
        mapper.get_metadata(context)

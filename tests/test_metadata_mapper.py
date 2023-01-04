import re

import pytest
from lambdas.lib.metadata_mapper import (
    ConfigSourceProvider,
    Context,
    MetadataMapper,
    PySourceProvider,
    Source
)
from lambdas.lib.metadata_mapper.format import Json
from lambdas.lib.metadata_mapper.storage import LocalFile


@pytest.fixture
def config():
    return {
        "sources": {
            "fixed_name_file": {
                "storage": {
                    "class": "LocalFile",
                    "name": "fixed_name_file.json"
                },
                "format": {
                    "class": "Json",
                }
            },
            "name_match_file": {
                "storage": {
                    "class": "LocalFile",
                    "name_match": r".*match_me\.json"
                },
                "format": {
                    "class": "Json"
                }
            }
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
            }
        }
    }


@pytest.fixture
def context(data_path):
    return Context(
        files={
            "fixed_name_file.json": {
                "path": str(data_path / "fixed_name_file.json")
            },
            "another_file.json": {},
            "yet_another_file.json": {},
            "first_match_me.json": {
                "path": str(data_path / "match_me.json")
            },
            "dont_match_me.json": {}
        }
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
        }
    }


def test_basic_py_source_provider(config, context):
    mapper = MetadataMapper(
        template=config["template"],
        source_provider=PySourceProvider({
            "fixed_name_file": Source(
                storage=LocalFile(
                    name="fixed_name_file.json"
                ),
                format=Json()
            ),
            "name_match_file": Source(
                storage=LocalFile(
                    name_match=r".*match_me\.json"
                ),
                format=Json()
            ),
            "name_match_file2": Source(
                storage=LocalFile(
                    name_match=re.compile(r".*match_me\.json")
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
        }
    }


def test_basic_s3_file(s3_resource, config, context):
    s3_resource.create_bucket(Bucket="test")
    s3_resource.Object("test", "fixed_name_file.json").put(
        Body=open(context.files["fixed_name_file.json"]["path"]).read()
    )
    context.files["fixed_name_file.json"]["s3uri"] = "s3://test/fixed_name_file.json"

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
        }
    }

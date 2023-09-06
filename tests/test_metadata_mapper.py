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
def fixed_name_file_config():
    return {
        "storage": {
            "class": "LocalFile",
            "filters": {
                "name": r"fixed_name_file\.json"
            }
        },
        "format": {
            "class": "Json",
        }
    }


@pytest.fixture
def config(fixed_name_file_config):
    return {
        "sources": {
            "fixed_name_file": fixed_name_file_config,
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
            "namespace_xml_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "xml_with_namespace.xml"
                    }
                },
                "format": {
                    "class": "Xml"
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
            },
            "namespace_xml_foobar_1": {
                "@mapped": {
                    "source": "namespace_xml_file",
                    "key": "./foo:foo/foo:bar[1]/foo:foobar"
                }
            },
            "namespace_xml_foobar_2": {
                "@mapped": {
                    "source": "namespace_xml_file",
                    "key": "./foo:foo/foo:bar[2]/foo:foobar"
                }
            },
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
                "name": "xml_with_namespace.xml",
                "path": str(data_path / "xml_with_namespace.xml")
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


def test_empty_context(fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "foo"
                }
            }
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config
        })
    )
    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "no files in context"
        )
    ):
        mapper.get_metadata(context)


@pytest.mark.xml
def test_basic(mapper, context):
    assert mapper.get_metadata(context) == {
        "foo": "value for foo",
        "outer": {
            "nested": "value for nested",
            "bar": "value for bar"
        },
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


@pytest.mark.xml
def test_mapped_key_callable(config, context):
    mapper = MetadataMapper(
        template={
            "bar": {
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
        "bar": "value for bar"
    }


def test_custom_directive(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "#mapped": {
                    "source": "fixed_name_file",
                    "key": "foo"
                }
            },
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config
        }),
        directive_marker="#"
    )
    assert mapper.get_metadata(context) == {
        "foo": "value for foo"
    }


@pytest.mark.xml
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
            "namespace_xml_file": Source(
                storage=LocalFile(
                    filters={
                        "name": "xml_with_namespace.xml"
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
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


@pytest.mark.xml
def test_basic_s3_file(s3_resource, config, context):
    s3_resource.create_bucket(Bucket="test")
    s3_resource.Object("test", "fixed_name_file.json").put(
        Body=open(context.files[0]["path"]).read()
    )
    context.files[0]["bucket"] = "test"
    context.files[0]["key"] = "fixed_name_file.json"

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
        "namespace_xml_foobar_1": "testing_1",
        "namespace_xml_foobar_2": "2",
        "xml_foobar_1": "testing_1",
        "xml_foobar_2": "2",
    }


def test_no_matching_files(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "source_file",
                    "key": "foo"
                }
            }
        },
        source_provider=ConfigSourceProvider({
            "source_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "does not exist"
                    }
                },
                "format": {
                    "class": "Json"
                }
            }
        })
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'source_file': "
            "no files matched filters"
        )
    ):
        mapper.get_metadata(context)


def test_source_non_existent_key(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "does_not_exist",
                }
            }
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config
        })
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to query source 'fixed_name_file': "
            "key not found 'does_not_exist'"
        ),
    ):
        mapper.get_metadata(context)


def test_mapped_non_existent_source(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "does not exist",
                    "key": "foo"
                }
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "source 'does not exist' does not exist"
        )
    ):
        mapper.get_metadata(context)


def test_mapped_missing_key(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                }
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "@mapped directive missing key: 'key'"
        )
    ):
        mapper.get_metadata(context)


def test_mapped_missing_source(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "key": "does not exist",
                }
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "@mapped directive missing key: 'source'"
        )
    ):
        mapper.get_metadata(context)


def test_mapped_missing_source_path(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "bar": [
                    "ignored",
                    "ignored",
                    {
                        "@mapped": {
                            "key": "does not exist",
                        }
                    }
                ]
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.bar\[2\]: "
            "@mapped directive missing key: 'source'"
        )
    ):
        mapper.get_metadata(context)


def test_mapped_missing_source_and_key(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {}
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "@mapped directive missing keys: 'key', 'source'"
        )
    ):
        mapper.get_metadata(context)


def test_mapped_extra_parameter(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "foo",
                    "does_not_exist": "does not exist",
                    "does_not_exist_2": "does not exist",
                }
            }
        },
        source_provider=ConfigSourceProvider({
            "fixed_name_file": fixed_name_file_config
        })
    )

    mapper.get_metadata(context) == {"foo": "value for foo"}


def test_invalid_directive(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@does_not_exist": {}
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "invalid directive '@does_not_exist'"
        )
    ):
        mapper.get_metadata(context)


def test_multiple_directives(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {},
                "@invalid": {}
            }
        },
        source_provider=ConfigSourceProvider({})
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo: "
            "multiple directives found in config: '@mapped', '@invalid'"
        )
    ):
        mapper.get_metadata(context)

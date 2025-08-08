import pytest

from mandible.metadata_mapper import (
    ConfigSourceProvider,
    Context,
    MetadataMapper,
    MetadataMapperError,
)


@pytest.mark.xml
def test_mapped_key_callable(config, context):
    mapper = MetadataMapper(
        template={
            "bar": {
                "@mapped": {
                    "source": "name_match_file",
                    "key": lambda ctx: ctx.meta["foo"],
                },
            },
        },
        source_provider=ConfigSourceProvider(config["sources"]),
    )
    context.meta["foo"] = "bar"

    assert mapper.get_metadata(context) == {
        "bar": "value for bar",
    }


def test_mapped_non_existent_source(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "does not exist",
                    "key": "foo",
                },
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@mapped: "
            "source 'does not exist' does not exist"
        ),
    ):
        mapper.get_metadata(context)


def test_mapped_missing_key(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                },
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@mapped: "
            "missing key: 'key'"
        ),
    ):
        mapper.get_metadata(context)


def test_mapped_missing_source(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {
                    "key": "does not exist",
                },
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@mapped: "
            "missing key: 'source'"
        ),
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
                        },
                    },
                ],
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.bar\[2\]\.@mapped: "
            "missing key: 'source'"
        ),
    ):
        mapper.get_metadata(context)


def test_mapped_missing_source_and_key(context):
    mapper = MetadataMapper(
        template={
            "foo": {
                "@mapped": {},
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to process template at \$\.foo\.@mapped: "
            "missing keys: 'key', 'source'"
        ),
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
                },
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "fixed_name_file": fixed_name_file_config,
            }
        ),
    )

    mapper.get_metadata(context) == {"foo": "value for foo"}


def test_reformatted_json_field_in_json():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Json",
                "value": {
                    "@mapped": {
                        "source": "file",
                        "key": "some-field",
                    },
                },
                "key": "foo",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": rb"""
                    {
                        "some-field": "{\"foo\": \"bar\"}"
                    }
                    """,
                    },
                    "format": {
                        "class": "Json",
                    },
                },
            }
        ),
    )

    context = Context()

    assert mapper.get_metadata(context) == "bar"


@pytest.mark.xml
def test_reformatted_json_field_in_xml():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Json",
                "value": {
                    "@mapped": {
                        "source": "file",
                        "key": "/root/json-field",
                    },
                },
                "key": "foo",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": b"""
                    <root>
                        <json-field>{"foo": "bar"}</json-field>
                    </root>
                    """,
                    },
                    "format": {
                        "class": "Xml",
                    },
                },
            }
        ),
    )

    context = Context()

    assert mapper.get_metadata(context) == "bar"


@pytest.mark.xml
def test_reformatted_json_field_in_xml_get_entire_value():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Json",
                "value": {
                    "@mapped": {
                        "source": "file",
                        "key": "/root/json-field",
                    },
                },
                "key": "$",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": b"""
                    <root>
                        <json-field>{"foo": "bar"}</json-field>
                    </root>
                    """,
                    },
                    "format": {
                        "class": "Xml",
                    },
                },
            }
        ),
    )

    context = Context()

    assert mapper.get_metadata(context) == {"foo": "bar"}


@pytest.mark.xml
def test_reformatted_xml_field_in_json():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Xml",
                "value": {
                    "@mapped": {
                        "source": "file",
                        "key": "foo",
                    },
                },
                "key": "/root/field",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": b"""
                    {
                        "foo": "<root><field>bar</field></root>"
                    }
                    """,
                    },
                    "format": {
                        "class": "Json",
                    },
                },
            }
        ),
    )

    context = Context()

    assert mapper.get_metadata(context) == "bar"


def test_reformatted_bad_type():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Json",
                "value": {
                    "@mapped": {
                        "source": "file",
                        "key": "foo",
                    },
                },
                "key": "$",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": b'{"foo": true}',
                    },
                    "format": {
                        "class": "Json",
                    },
                },
            }
        ),
    )

    context = Context()

    with pytest.raises(MetadataMapperError, match="but got 'bool'"):
        mapper.get_metadata(context)


@pytest.mark.xml
def test_reformatted_nested():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Xml",
                "value": {
                    "@reformatted": {
                        "format": "Json",
                        "value": '{"foo": "<root><field>bar</field></root>"}',
                        "key": "foo",
                    },
                },
                "key": "/root/field",
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "file": {
                    "storage": {
                        "class": "Dummy",
                        "data": b"""
                    {
                        "foo": "<root><field>bar</field></root>"
                    }
                    """,
                    },
                    "format": {
                        "class": "Json",
                    },
                },
            }
        ),
    )

    context = Context()

    assert mapper.get_metadata(context) == "bar"


def test_reformatted_nested_missing_parameter():
    mapper = MetadataMapper(
        template={
            "@reformatted": {
                "format": "Json",
                "value": {
                    "@reformatted": {
                        "format": "Json",
                        "key": "foo",
                    },
                },
                "key": "/root/field",
            },
        },
        source_provider=ConfigSourceProvider({}),
    )

    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            "failed to process template at "
            r"\$\.@reformatted\.value\.@reformatted: "
            "missing key: 'value'"
        ),
    ):
        mapper.get_metadata(context)


def test_add_constant_values():
    mapper = MetadataMapper(
        template={
            "integers": {
                "@add": {
                    "left": 1,
                    "right": 2,
                },
            },
            "floats": {
                "@add": {
                    "left": 1.5,
                    "right": 2,
                },
            },
            "strings": {
                "@add": {
                    "left": "hello ",
                    "right": "world",
                },
            },
            "lists": {
                "@add": {
                    "left": [1, 2],
                    "right": [3, 4],
                },
            },
        },
    )

    context = Context()

    assert mapper.get_metadata(context) == {
        "integers": 3,
        "floats": 3.5,
        "strings": "hello world",
        "lists": [1, 2, 3, 4],
    }


def test_add_constant_values_bad_types():
    mapper = MetadataMapper(
        template={
            "@add": {
                "left": "foo",
                "right": 10,
            },
        },
    )

    context = Context()

    with pytest.raises(
        MetadataMapperError,
        match=(
            r"failed to evaluate template: failed to call directive at \$\.@add: "
            r'can only concatenate str \(not "int"\) to str'
        ),
    ):
        mapper.get_metadata(context)


def test_add_mapped_values(context, fixed_name_file_config):
    mapper = MetadataMapper(
        template={
            "@add": {
                "left": {
                    "@mapped": {
                        "source": "fixed_name_file",
                        "key": "foo",
                    },
                },
                "right": {
                    "@mapped": {
                        "source": "fixed_name_file",
                        "key": "nested.key",
                    },
                },
            },
        },
        source_provider=ConfigSourceProvider(
            {
                "fixed_name_file": fixed_name_file_config,
            }
        ),
    )

    assert mapper.get_metadata(context) == "value for foovalue for nested"

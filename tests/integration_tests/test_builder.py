import pytest

from mandible.metadata_mapper import ConfigSourceProvider, MetadataMapper
from mandible.metadata_mapper.builder import (
    add,
    build,
    floordiv,
    mapped,
    mul,
    or_,
    sub,
    truediv,
)


@pytest.fixture
def source_provider(config):
    return ConfigSourceProvider(
        {
            "fixed_name_file": config["sources"]["fixed_name_file"],
            "name_match_file": config["sources"]["name_match_file"],
        },
    )


def test_template_operations(source_provider, context):
    mapper = MetadataMapper(
        template=build(
            {
                "add": {
                    "list": (
                        mapped("fixed_name_file", "list")
                        # ruff hint
                        + mapped("name_match_file", "list")
                    ),
                    "list_const": mapped("fixed_name_file", "list") + [4, 5],
                    "list_const_r": [0, 1] + mapped("fixed_name_file", "list"),
                    "number": mapped("fixed_name_file", "integer") + 20.5,
                    "string": mapped("fixed_name_file", "foo") + "bar",
                    "constant": add(10, 7),
                },
                "floordiv": {
                    "number": mapped("fixed_name_file", "integer") // 3,
                    "number_r": 237 // mapped("fixed_name_file", "integer"),
                    "constant": floordiv(10, 7),
                },
                "mul": {
                    "number": mapped("fixed_name_file", "integer") * 3,
                    "number_r": 1.5 * mapped("fixed_name_file", "integer"),
                    "string": mapped("fixed_name_file", "foo") * 2,
                    "constant": mul(10, 7),
                },
                "or": {
                    "number": or_(
                        mapped("fixed_name_file", "zero"),
                        mapped("fixed_name_file", "integer"),
                    ),
                    "number_method": mapped("fixed_name_file", "zero").or_(
                        mapped("fixed_name_file", "integer"),
                    ),
                    "bool": mapped("fixed_name_file", "bool").or_(True),
                    "string": mapped("fixed_name_file", "empty-string").or_("Unknown"),
                    "constant": or_(False, "foobar"),
                    "missing_key": or_(
                        mapped("fixed_name_file", "does-not-exist", default=None),
                        mapped("fixed_name_file", "foo"),
                    ),
                },
                "sub": {
                    "number": mapped("fixed_name_file", "integer") - 3,
                    "number_r": 1.5 - mapped("fixed_name_file", "integer"),
                    "constant": sub(10, 7),
                },
                "truediv": {
                    "number": mapped("fixed_name_file", "integer") / 3,
                    "number_r": 237 / mapped("fixed_name_file", "integer"),
                    "constant": truediv(10, 7),
                },
            },
        ),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "add": {
            "list": [1, 2, 3, "A", "B", "C"],
            "list_const": [1, 2, 3, 4, 5],
            "list_const_r": [0, 1, 1, 2, 3],
            "number": 30.5,
            "string": "value for foobar",
            "constant": 17,
        },
        "floordiv": {
            "number": 3,
            "number_r": 23,
            "constant": 1,
        },
        "mul": {
            "number": 30,
            "number_r": 15.0,
            "string": "value for foovalue for foo",
            "constant": 70,
        },
        "or": {
            "number": 10,
            "number_method": 10,
            "bool": True,
            "string": "Unknown",
            "constant": "foobar",
            "missing_key": "value for foo",
        },
        "sub": {
            "number": 7,
            "number_r": -8.5,
            "constant": 3,
        },
        "truediv": {
            "number": 3.3333333333333335,
            "number_r": 23.7,
            "constant": 1.4285714285714286,
        },
    }


def test_template_default(source_provider, context):
    mapper = MetadataMapper(
        template=build(
            {
                "badkey": mapped("fixed_name_file", "badkey", default=None),
            },
        ),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "badkey": None,
    }


def test_template_default_multiple_build(source_provider, context):
    base_template = build(
        {
            "badkey": mapped("fixed_name_file", "badkey", default=None),
        },
    )
    mapper = MetadataMapper(
        template=build(
            {
                **base_template,
                "goodkey": mapped("fixed_name_file", "integer"),
            },
        ),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "badkey": None,
        "goodkey": 10,
    }

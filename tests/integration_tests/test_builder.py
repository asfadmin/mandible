import pytest

from mandible.metadata_mapper import ConfigSourceProvider, MetadataMapper
from mandible.metadata_mapper.builder import build, mapped


@pytest.fixture
def source_provider(config):
    return ConfigSourceProvider({
        "fixed_name_file": config["sources"]["fixed_name_file"],
        "name_match_file": config["sources"]["name_match_file"],
    })


def test_template(source_provider, context):
    mapper = MetadataMapper(
        template=build({
            "list": (
                mapped("fixed_name_file", "list")
                + mapped("name_match_file", "list")
            ),
            "number": mapped("fixed_name_file", "integer") + 20.5,
        }),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "list": [1, 2, 3, "A", "B", "C"],
        "number": 30.5,
    }


def test_template_default(source_provider, context):
    mapper = MetadataMapper(
        template=build({
            "badkey": mapped("fixed_name_file", "badkey", default=None),
        }),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "badkey": None,
    }


def test_template_default_multiple_build(source_provider, context):
    base_template = build({
        "badkey": mapped("fixed_name_file", "badkey", default=None),
    })
    mapper = MetadataMapper(
        template=build({
            **base_template,
            "goodkey": mapped("fixed_name_file", "integer"),
        }),
        source_provider=source_provider,
    )

    assert mapper.get_metadata(context) == {
        "badkey": None,
        "goodkey": 10,
    }

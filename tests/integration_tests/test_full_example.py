import pytest

from mandible.metadata_mapper import ConfigSourceProvider, Context, MetadataMapper
from mandible.metadata_mapper.builder import build, mapped

pytestmark = [pytest.mark.jsonpath, pytest.mark.xml]


@pytest.fixture
def sources():
    return {
        "json": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": "$.meta.json_file_name",
                },
            },
            "format": {
                "class": "Json",
            },
        },
        "xml": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": r"example\.xml",
                },
            },
            "format": {
                "class": "Xml",
            },
        },
        "bzip2json": {
            "storage": {
                "class": "LocalFile",
                "filters": {
                    "name": r"example\.json\.bz2",
                },
            },
            "format": {
                "class": "Bzip2File",
                "format": {
                    "class": "Json",
                },
            },
        },
    }


@pytest.fixture
def template():
    return build(
        {
            "JsonMd": {
                # Simple queries
                "description": mapped("json", "description"),
                "total": mapped("json", "meta.summary.total"),
                "complete": mapped("json", "meta.summary.complete"),
                "null": mapped("json", "meta.null"),
                # JSONPath only queries
                "banana_price": mapped("json", "inventory[?name = 'Banana'].price"),
                "oreo_price": mapped(
                    "json",
                    "inventory[?name = 'Oreo'].price",
                    default=4.49,
                ),
                "first_red_item": mapped(
                    "json",
                    "inventory[?attributes.color = 'red'].name",
                    return_first=True,
                ),
                "in_stock_items": mapped(
                    "json",
                    "inventory[?in_stock = true].name",
                    return_list=True,
                ),
            },
            "XmlMd": {
                "description": mapped("xml", "./description"),
                "total": mapped("xml", "./meta/summary/total"),
                "complete": mapped("xml", "./meta/summary/complete"),
                "null": mapped("xml", "./meta/null"),
                "banana_price": mapped("xml", "./inventory/item[name='Banana']/price"),
                "oreo_price": mapped(
                    "xml",
                    "./inventory/item[name='Oreo']/price",
                    default=4.49,
                ),
                "first_red_item": mapped(
                    "xml",
                    "./inventory/item[attributes/color='red']/name",
                    return_first=True,
                ),
                "in_stock_items": mapped(
                    "xml",
                    "./inventory/item[in_stock='true']/name",
                    return_list=True,
                ),
            },
            "Bzip2JsonMd": {
                "description": mapped("bzip2json", "description"),
                "total": mapped("bzip2json", "meta.summary.total"),
                "complete": mapped("bzip2json", "meta.summary.complete"),
                "null": mapped("bzip2json", "meta.null"),
                # JSONPath only queries
                "banana_price": mapped("bzip2json", "inventory[?name = 'Banana'].price"),
                "oreo_price": mapped(
                    "bzip2json",
                    "inventory[?name = 'Oreo'].price",
                    default=4.49,
                ),
                "first_red_item": mapped(
                    "bzip2json",
                    "inventory[?attributes.color = 'red'].name",
                    return_first=True,
                ),
                "in_stock_items": mapped(
                    "bzip2json",
                    "inventory[?in_stock = true].name",
                    return_list=True,
                ),
            },
        },
    )


@pytest.fixture
def context(data_path):
    return Context(
        files=[
            {
                "name": f"example.{ext}",
                "path": str(data_path / f"example.{ext}"),
            }
            for ext in ("json", "json.bz2", "xml", "h5")
        ],
        meta={
            "json_file_name": r"example\.json",
        },
    )


def test_full_example(context, sources, template):
    mapper = MetadataMapper(
        template=template,
        source_provider=ConfigSourceProvider(sources),
    )

    assert mapper.get_metadata(context) == {
        "JsonMd": {
            "description": "A store inventory",
            "total": 5,
            "complete": False,
            "null": None,
            "banana_price": 0.99,
            "oreo_price": 4.49,
            "first_red_item": "Apple",
            "in_stock_items": ["Apple", "Banana", "Tomato", "Scotch Tape", "Oreo"],
        },
        "XmlMd": {
            "description": "A store inventory",
            "total": "5",
            "complete": "false",
            "null": None,
            "banana_price": "0.99",
            "oreo_price": 4.49,
            "first_red_item": "Apple",
            "in_stock_items": ["Apple", "Banana", "Tomato", "Scotch Tape", "Oreo"],
        },
        "Bzip2JsonMd": {
            "description": "A store inventory",
            "total": 5,
            "complete": False,
            "null": None,
            "banana_price": 0.99,
            "oreo_price": 4.49,
            "first_red_item": "Apple",
            "in_stock_items": ["Apple", "Banana", "Tomato", "Scotch Tape", "Oreo"],
        },
    }

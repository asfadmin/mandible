import pytest

from mandible.metadata_mapper import Context


@pytest.fixture
def fixed_name_file_config():
    return {
        "storage": {
            "class": "LocalFile",
            "filters": {
                "name": r"fixed_name_file\.json",
            },
        },
        "format": {
            "class": "Json",
        },
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
                        "name": r".*match_me\.json",
                    },
                },
                "format": {
                    "class": "Json",
                },
            },
            "fixed_xml_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "fixed_xml_file.xml",
                    },
                },
                "format": {
                    "class": "Xml",
                },
            },
            "namespace_xml_file": {
                "storage": {
                    "class": "LocalFile",
                    "filters": {
                        "name": "xml_with_namespace.xml",
                    },
                },
                "format": {
                    "class": "Xml",
                },
            },
        },
        "template": {
            "foo": {
                "@mapped": {
                    "source": "fixed_name_file",
                    "key": "foo",
                },
            },
            "outer": {
                "nested": {
                    "@mapped": {
                        "source": "fixed_name_file",
                        "key": "nested.key",
                    },
                },
                "bar": {
                    "@mapped": {
                        "source": "name_match_file",
                        "key": "bar",
                    },
                },
            },
            "xml_foobar_1": {
                "@mapped": {
                    "source": "fixed_xml_file",
                    "key": "./foo/bar[1]/foobar",
                },
            },
            "xml_foobar_2": {
                "@mapped": {
                    "source": "fixed_xml_file",
                    "key": "./foo/bar[2]/foobar",
                },
            },
            "namespace_xml_foobar_1": {
                "@mapped": {
                    "source": "namespace_xml_file",
                    "key": "./foo:foo/foo:bar[1]/foo:foobar",
                },
            },
            "namespace_xml_foobar_2": {
                "@mapped": {
                    "source": "namespace_xml_file",
                    "key": "./foo:foo/foo:bar[2]/foo:foobar",
                },
            },
        },
    }


@pytest.fixture
def context(data_path):
    return Context(
        files=[
            {
                "name": "fixed_name_file.json",
                "path": str(data_path / "fixed_name_file.json"),
            },
            {
                "name": "fixed_xml_file.xml",
                "path": str(data_path / "fixed_xml_file.xml"),
            },
            {
                "name": "xml_with_namespace.xml",
                "path": str(data_path / "xml_with_namespace.xml"),
            },
            {
                "name": "another_file.json",
            },
            {
                "name": "yet_another_file.json",
            },
            {
                "name": "first_match_me.json",
                "path": str(data_path / "match_me.json"),
            },
            {
                "name": "dont_match_me.json",
            },
        ],
    )

import io

import pytest

from mandible.metadata_mapper.format import (
    FORMAT_REGISTRY,
    H5,
    Format,
    FormatError,
    Json,
    Xml,
)

try:
    import h5py
except ImportError:
    h5py = None


def test_registry():
    assert FORMAT_REGISTRY == {
        "H5": H5,
        "Json": Json,
        "Xml": Xml,
    }


def test_registry_intermediate_class():
    class Foo(Format, register=False):
        pass

    assert "Foo" not in FORMAT_REGISTRY


def test_registry_error():
    with pytest.raises(KeyError):
        FORMAT_REGISTRY["FooBarBaz"]


@pytest.mark.h5
def test_h5():
    file = io.BytesIO()
    with h5py.File(file, "w") as f:
        f["foo"] = "foo value"
        f["bar"] = "bar value"
        f["list"] = ["list", "value"]
        nested = f.create_group("nested")
        nested["qux"] = "qux nested value"

    format = H5()

    assert format.get_values(
        file,
        ["/foo", "bar", "list", "nested/qux"]
    ) == {
        "/foo": "foo value",
        "bar": "bar value",
        "list": ["list", "value"],
        "nested/qux": "qux nested value"
    }


@pytest.mark.h5
def test_h5_empty_key():
    file = io.BytesIO()
    with h5py.File(file, "w") as f:
        f["foo"] = "foo value"
        f["bar"] = "bar value"

    format = H5()

    with pytest.raises(FormatError, match="key not found ''"):
        format.get_value(file, "")


@pytest.mark.h5
def test_h5_key_error():
    file = io.BytesIO()
    with h5py.File(file, "w"):
        pass

    format = H5()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, ["foo"])


def test_json():
    file = io.BytesIO(b"""
    {
        "foo": "foo value",
        "bar": "bar value",
        "list": ["list", "value"],
        "nested": {
            "qux": "qux nested value"
        }
    }
    """)
    format = Json()

    assert format.get_values(
        file,
        ["foo", "bar", "list", "nested.qux"]
    ) == {
        "foo": "foo value",
        "bar": "bar value",
        "list": ["list", "value"],
        "nested.qux": "qux nested value"
    }


def test_json_dollar_key():
    file = io.BytesIO(b"""
    {
        "foo": "foo value",
        "bar": "bar value"
    }
    """)
    format = Json()

    assert format.get_value(file, "$") == {
        "foo": "foo value",
        "bar": "bar value",
    }


def test_json_key_error():
    file = io.BytesIO(b"{}")
    format = Json()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, ["foo"])


@pytest.mark.xml
def test_xml():
    file = io.BytesIO(b"""
    <root>
        <foo>foo value</foo>
        <bar>bar value</bar>
        <list>
            <v>list</v>
            <v>value</v>
        </list>
        <nested>
            <qux>qux nested value</qux>
        </nested>
    </root>
    """)
    format = Xml()

    # TODO(reweeden): Selecting lists is not supported
    assert format.get_values(
        file,
        ["/root/foo", "./bar", "./list/v[2]", "./nested/qux"]
    ) == {
        "/root/foo": "foo value",
        "./bar": "bar value",
        "./list/v[2]": "value",
        "./nested/qux": "qux nested value"
    }


@pytest.mark.xml
def test_xml_empty_key():
    file = io.BytesIO(b"""
    <root>
        <foo>foo value</foo>
        <bar>bar value</bar>
    </root>
    """)
    format = Xml()

    assert format.get_values(file, "") == {}


@pytest.mark.xml
def test_namespace_xml():
    file = io.BytesIO(b"""
    <root xmlns:foo="http://bigtest.com/namespace/docs">
        <foo:foo>foo value</foo:foo>
        <foo:bar>bar value</foo:bar>
        <list>
            <foo:v>list</foo:v>
            <foo:v>value</foo:v>
        </list>
        <foo:nested>
            <foo:qux>qux nested value</foo:qux>
        </foo:nested>
    </root>
    """)
    format = Xml()

    # TODO(reweeden): Selecting lists is not supported
    assert format.get_values(
        file,
        ["/root/foo:foo", "./foo:bar", "./list/foo:v[2]", "./foo:nested/foo:qux"]
    ) == {
        "/root/foo:foo": "foo value",
        "./foo:bar": "bar value",
        "./list/foo:v[2]": "value",
        "./foo:nested/foo:qux": "qux nested value"
    }


@pytest.mark.xml
def test_xml_key_error():
    file = io.BytesIO(b"<root></root>")

    format = Xml()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, ["foo"])

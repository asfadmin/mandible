import io

import h5py
import pytest

from mandible.metadata_mapper.format import H5, Format, FormatError, Json, Xml


def test_registry():
    assert Format.get_subclass("H5") is H5
    assert Format.get_subclass("Json") is Json
    assert Format.get_subclass("Xml") is Xml


def test_registry_error():
    with pytest.raises(KeyError):
        Format.get_subclass("FooBarBaz")


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


def test_h5_key_error():
    file = io.BytesIO()
    with h5py.File(file, "w"):
        pass

    format = H5()

    with pytest.raises(FormatError, match="Key not found 'foo'"):
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


def test_json_key_error():
    file = io.BytesIO(b"{}")
    format = Json()

    with pytest.raises(FormatError, match="Key not found 'foo'"):
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


def test_xml_key_error():
    file = io.BytesIO(b"<root></root>")

    format = Xml()

    with pytest.raises(FormatError, match="Key not found 'foo'"):
        format.get_values(file, ["foo"])

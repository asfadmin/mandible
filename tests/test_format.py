import io
import zipfile
from unittest import mock

import pytest

from mandible.metadata_mapper.format import (
    FORMAT_REGISTRY,
    H5,
    Format,
    FormatError,
    Json,
    Xml,
    ZipInfo,
    ZipMember,
)
from mandible.metadata_mapper.key import Key

try:
    import h5py
except ImportError:
    h5py = None


def test_registry():
    assert FORMAT_REGISTRY == {
        "H5": H5,
        "Json": Json,
        "Xml": Xml,
        "ZipInfo": ZipInfo,
        "ZipMember": ZipMember,
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
        [Key("/foo"), Key("bar"), Key("list"), Key("nested/qux")],
    ) == {
        Key("/foo"): "foo value",
        Key("bar"): "bar value",
        Key("list"): ["list", "value"],
        Key("nested/qux"): "qux nested value",
    }


@pytest.mark.h5
def test_h5_optional_key():
    file = io.BytesIO()
    with h5py.File(file, "w") as f:
        f["foo"] = "foo value"

    format = H5()
    bar_value = "bar value"

    assert format.get_value(file, Key("bar", default=None)) is None
    file.seek(0)
    assert format.get_value(file, Key("bar", default=bar_value)) == bar_value


@pytest.mark.h5
def test_h5_empty_key():
    file = io.BytesIO()
    with h5py.File(file, "w") as f:
        f["foo"] = "foo value"
        f["bar"] = "bar value"

    format = H5()

    with pytest.raises(FormatError, match="key not found ''"):
        format.get_value(file, Key(""))


@pytest.mark.h5
def test_h5_key_error():
    file = io.BytesIO()
    with h5py.File(file, "w"):
        pass

    format = H5()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, [Key("foo")])


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
        [Key("foo"), Key("bar"), Key("list"), Key("nested.qux")],
    ) == {
        Key("foo"): "foo value",
        Key("bar"): "bar value",
        Key("list"): ["list", "value"],
        Key("nested.qux"): "qux nested value",
    }


def test_json_dollar_key():
    file = io.BytesIO(b"""
    {
        "foo": "foo value",
        "bar": "bar value"
    }
    """)
    format = Json()

    assert format.get_value(file, Key("$")) == {
        "foo": "foo value",
        "bar": "bar value",
    }


def test_json_optional_key():
    file = io.BytesIO(b"""
    {
        "foo": "foo value"
    }
    """)
    format = Json()
    bar_value = "bar value"

    assert format.get_value(file, Key("bar", default=None)) is None
    file.seek(0)
    assert format.get_value(file, Key("bar", default=bar_value)) == bar_value


def test_json_key_error():
    file = io.BytesIO(b"{}")
    format = Json()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, [Key("foo")])


def test_zip():
    file = io.BytesIO()
    with zipfile.ZipFile(file, "w") as f:
        f.writestr(
            "foo",
            b"""
            {
                "foo": "foo value",
                "bar": "bar value"
            }
            """,
        )

    format = ZipMember(
        filters={
            "filename": "foo",
        },
        format=Json(),
    )

    assert format.get_value(file, Key("$")) == {
        "foo": "foo value",
        "bar": "bar value",
    }


def test_zip_filters():
    file = io.BytesIO()
    with zipfile.ZipFile(file, "w") as f:
        f.writestr("unformatted.txt", "This is just some text")
        f.writestr("foobar.txt", "This is some foo text")
        f.writestr(
            "foo",
            b"""
            {
                "foo": "foo value",
                "bar": "bar value"
            }
            """,
        )

    format = ZipMember(
        filters={
            "filename": "^foo$",
        },
        format=Json(),
    )

    assert format.get_value(file, Key("$")) == {
        "foo": "foo value",
        "bar": "bar value",
    }


def test_zip_filters_bad_attribute():
    file = io.BytesIO()
    with zipfile.ZipFile(file, "w") as f:
        f.writestr("unformatted.txt", "This is just some text/n")
        f.writestr("foobar.txt", "This is some foo text")

    format = ZipMember(
        filters={
            "filename": "^foo$",
            "nonexistent_attr": True,
        },
        format=Json(),
    )

    with pytest.raises(FormatError, match="no archive members matched filters"):
        format.get_value(file, Key("key"))


def test_zipinfo():
    file = io.BytesIO()
    with zipfile.ZipFile(file, "w") as f:
        f.writestr("unformatted.txt", "This is just some text")
        f.writestr("foobar.txt", "This is some foo text")
        f.writestr("foo.json", '{"foo": "bar"}')

    format = ZipInfo()

    assert format.get_value(file, Key("filename")) is None


@pytest.mark.jsonpath
def test_zipinfo_jsonpath():
    file = io.BytesIO()
    with zipfile.ZipFile(file, "w") as f:
        f.writestr("unformatted.txt", "This is just some text")
        f.writestr("foobar.txt", "This is some foo text")
        f.writestr("foo.json", '{"foo": "bar"}')

    format = ZipInfo()

    assert format.get_value(file, Key("infolist[1].compress_size")) == 21
    assert format.get_value(file, Key("infolist[1]")) == {
        "CRC": 3800794396,
        "comment": b"",
        "compress_size": 21,
        "compress_type": 0,
        "create_system": 3,
        "create_version": 20,
        "date_time": mock.ANY,
        "external_attr": 25165824,
        "extra": b"",
        "extract_version": 20,
        "file_size": 21,
        "filename": "foobar.txt",
        "flag_bits": 0,
        "header_offset": 67,
        "internal_attr": 0,
        "orig_filename": "foobar.txt",
        "reserved": 0,
        "volume": 0,
    }


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

    assert format.get_values(
        file,
        [
            Key("/root/foo"),
            Key("./bar"),
            Key("./list/v[2]"),
            Key("./nested/qux"),
            Key("./list/v", return_list=True),
            Key("./list/v", return_first=True),
            Key("count(./list/v)"),
        ],
    ) == {
        Key("/root/foo"): "foo value",
        Key("./bar"): "bar value",
        Key("./list/v[2]"): "value",
        Key("./nested/qux"): "qux nested value",
        Key("./list/v", return_list=True): ["list", "value"],
        Key("./list/v", return_first=True): "list",
        Key("count(./list/v)"): 2,
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

    with pytest.raises(FormatError, match="'' Invalid expression"):
        assert format.get_values(file, [Key("")]) == {}


@pytest.mark.xml
def test_xml_optional_key():
    file = io.BytesIO(b"""
    <root>
        <foo>foo value</foo>
    </root>
    """)

    format = Xml()
    bar_value = "bar value"

    assert format.get_value(file, Key("bar", default=None)) is None
    file.seek(0)
    assert format.get_value(file, Key("bar", default=bar_value)) == bar_value


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

    assert format.get_values(
        file,
        [
            Key("/root/foo:foo"),
            Key("./foo:bar"),
            Key("./list/foo:v[2]"),
            Key("./foo:nested/foo:qux"),
            Key("./list/foo:v", return_list=True),
            Key("./list/foo:v", return_first=True),
        ],
    ) == {
        Key("/root/foo:foo"): "foo value",
        Key("./foo:bar"): "bar value",
        Key("./list/foo:v[2]"): "value",
        Key("./foo:nested/foo:qux"): "qux nested value",
        Key("./list/foo:v", return_list=True): ["list", "value"],
        Key("./list/foo:v", return_first=True): "list",
    }


@pytest.mark.xml
def test_xml_key_error():
    file = io.BytesIO(b"<root></root>")

    format = Xml()

    with pytest.raises(FormatError, match="key not found 'foo'"):
        format.get_values(file, [Key("foo")])

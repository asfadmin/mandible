import pytest

from mandible.cumulus.ingest.url_path_template import url_path_template


def test_noop():
    assert url_path_template("foo", {}) == "foo"
    assert url_path_template("foo", {"foo": "bar"}) == "foo"


def test_simple_replace():
    assert url_path_template("{foo}", {"foo": "test"}) == "test"
    assert url_path_template("foo/{bar}", {"bar": "test"}) == "foo/test"
    assert url_path_template(
        "foo/{bar}/{bar}",
        {"bar": "test"},
    ) == "foo/test/test"
    assert url_path_template(
        "foo/{bar}/{baz}",
        {"bar": "test", "baz": "many"},
    ) == "foo/test/many"


def test_jsonpath_dot_syntax():
    assert url_path_template("{foo.bar}", {"foo": {"bar": "test"}}) == "test"
    assert url_path_template(
        "{foo.bar.baz}",
        {"foo": {"bar": {"baz": "test"}}},
    ) == "test"


@pytest.mark.jsonpath
def test_jsonpath():
    assert url_path_template(
        "{foo.bar[1].baz}",
        {
            "foo": {
                "bar": [
                    {"ignore": "me"},
                    {"baz": "test"},
                ],
            },
        },
    ) == "test"

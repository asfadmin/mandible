from mandible import jsonpath


def test_get_simple():
    data = {
        "number": 1,
        "foo": {
            "bar": {
                "baz": "string-value",
            },
        },
    }

    assert jsonpath.get(data, "$") == [data]
    assert jsonpath.get(data, "number") == [1]
    assert jsonpath.get(data, "$.number") == [1]
    assert jsonpath.get(data, "foo.bar.baz") == ["string-value"]
    assert jsonpath.get(data, "$.foo.bar.baz") == ["string-value"]

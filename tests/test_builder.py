from mandible.metadata_mapper.builder import build, mapped, reformatted


def test_build_noop():
    template = {
        "something": ["simple"],
        "with": {
            "nested": [
                {"data": ["structures"]},
            ],
        },
    }

    assert build(template) == template


def test_build_mapped():
    template = mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@mapped": {
            "source": "some_source",
            "key": "some.key",
        },
    }


def test_build_directive_marker():
    template = mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template, directive_marker="#%^") == {
        "#%^mapped": {
            "source": "some_source",
            "key": "some.key",
        },
    }


def test_build_reformatted():
    template = reformatted(
        format="Json",
        value=mapped(
            source="some_source",
            key="some.key",
        ),
        key="foo",
    )

    assert build(template) == {
        "@reformatted": {
            "format": "Json",
            "value": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "key": "foo",
        },
    }

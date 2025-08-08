from mandible.metadata_mapper.builder import (
    add,
    build,
    floordiv,
    mapped,
    mul,
    reformatted,
    sub,
    truediv,
)


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


def test_build_mapped_key_options():
    template = mapped(
        source="some_source",
        key="some.key",
        return_list=True,
    )

    assert build(template) == {
        "@mapped": {
            "source": "some_source",
            "key": "some.key",
            "key_options": {
                "return_list": True,
            },
        },
    }


def test_build_mapped_optional_key():
    template = mapped(
        source="some_source",
        key="some.key",
        default="some value",
    )

    assert build(template) == {
        "@mapped": {
            "source": "some_source",
            "key": "some.key",
            "key_options": {
                "default": "some value",
            },
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


def test_build_reformatted_key_options():
    template = reformatted(
        format="Json",
        value=mapped(
            source="some_source",
            key="some.key",
        ),
        key="foo",
        return_list=True,
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
            "key_options": {
                "return_list": True,
            },
        },
    }


def test_build_add():
    template = add(
        left=1,
        right=2,
    )

    assert build(template) == {
        "@add": {
            "left": 1,
            "right": 2,
        },
    }


def test_build_add_automatic():
    template = (
        mapped(
            source="some_source",
            key="some.key",
        )
        + 10
    )

    assert build(template) == {
        "@add": {
            "left": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "right": 10,
        },
    }


def test_build_add_automatic_right():
    template = 10 + mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@add": {
            "left": 10,
            "right": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
        },
    }


def test_build_floordiv():
    template = floordiv(
        left=1,
        right=2,
    )

    assert build(template) == {
        "@floordiv": {
            "left": 1,
            "right": 2,
        },
    }


def test_build_floordiv_automatic():
    template = (
        mapped(
            source="some_source",
            key="some.key",
        )
        // 10
    )

    assert build(template) == {
        "@floordiv": {
            "left": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "right": 10,
        },
    }


def test_build_floordiv_automatic_right():
    template = 10 // mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@floordiv": {
            "left": 10,
            "right": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
        },
    }


def test_build_mul():
    template = mul(
        left=1,
        right=2,
    )

    assert build(template) == {
        "@mul": {
            "left": 1,
            "right": 2,
        },
    }


def test_build_mul_automatic():
    template = (
        mapped(
            source="some_source",
            key="some.key",
        )
        * 10
    )

    assert build(template) == {
        "@mul": {
            "left": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "right": 10,
        },
    }


def test_build_mul_automatic_right():
    template = 10 * mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@mul": {
            "left": 10,
            "right": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
        },
    }


def test_build_sub():
    template = sub(
        left=1,
        right=2,
    )

    assert build(template) == {
        "@sub": {
            "left": 1,
            "right": 2,
        },
    }


def test_build_sub_automatic():
    template = (
        mapped(
            source="some_source",
            key="some.key",
        )
        - 10
    )

    assert build(template) == {
        "@sub": {
            "left": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "right": 10,
        },
    }


def test_build_sub_automatic_right():
    template = 10 - mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@sub": {
            "left": 10,
            "right": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
        },
    }


def test_build_truediv():
    template = truediv(
        left=1,
        right=2,
    )

    assert build(template) == {
        "@truediv": {
            "left": 1,
            "right": 2,
        },
    }


def test_build_truediv_automatic():
    template = (
        mapped(
            source="some_source",
            key="some.key",
        )
        / 10
    )

    assert build(template) == {
        "@truediv": {
            "left": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
            "right": 10,
        },
    }


def test_build_truediv_automatic_right():
    template = 10 / mapped(
        source="some_source",
        key="some.key",
    )

    assert build(template) == {
        "@truediv": {
            "left": 10,
            "right": {
                "@mapped": {
                    "source": "some_source",
                    "key": "some.key",
                },
            },
        },
    }

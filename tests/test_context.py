from dataclasses import dataclass, field
from typing import Optional

import pytest

from mandible.metadata_mapper.context import (
    Context,
    ContextValue,
    replace_context_values,
)
from mandible.metadata_mapper.exception import ContextValueError


@dataclass
class Dummy:
    x: int
    list_value: list = field(default_factory=list)
    dict_value: dict = field(default_factory=dict)
    recursive: Optional["Dummy"] = None


@pytest.fixture
def context():
    return Context(
        meta={
            "foo": "foo-value",
            "bar": "bar-value",
            "a-number": 1,
            "a-list": [1, 2, 3],
            "a-dict": {"a": 1, "b": 2},
        },
    )


def test_replace_context_values_noop(context):
    # Certain objects should be passed through completely unchanged
    for obj in (
        1,
        2.5,
        "foo",
        True,
        None,
        object(),
    ):
        assert replace_context_values(obj, context) is obj

    # Nested structures will be copied, but should compare equal
    for obj in (
        [1, 2, 3],
        {"a": 1, "b": 2, "c": 3},
        Dummy(x=1),
    ):
        assert replace_context_values(obj, context) == obj


def test_replace_context_values_direct(context):
    assert replace_context_values(
        ContextValue("$.meta.foo"),
        context,
    ) == "foo-value"
    assert replace_context_values(
        ContextValue("$.meta.bar"),
        context,
    ) == "bar-value"
    assert replace_context_values(
        ContextValue("$.meta.a-number"),
        context,
    ) == 1
    assert replace_context_values(
        ContextValue("$.meta.a-list"),
        context,
    ) == [1, 2, 3]
    assert replace_context_values(
        ContextValue("$.meta.a-dict"),
        context,
    ) == {"a": 1, "b": 2}


def test_replace_context_values_nested(context):
    # 1 level
    assert replace_context_values(
        {"foo": ContextValue("$.meta.foo")},
        context,
    ) == {"foo": "foo-value"}
    assert replace_context_values(
        [ContextValue("$.meta.foo")],
        context,
    ) == ["foo-value"]
    assert replace_context_values(
        Dummy(x=ContextValue("$.meta.a-number")),
        context,
    ) == Dummy(x=1)

    # 2 levels
    assert replace_context_values(
        {"foo": {"bar": ContextValue("$.meta.bar")}},
        context,
    ) == {"foo": {"bar": "bar-value"}}
    assert replace_context_values(
        [[ContextValue("$.meta.foo")]],
        context,
    ) == [["foo-value"]]
    assert replace_context_values(
        Dummy(x=2, recursive=Dummy(x=ContextValue("$.meta.a-number"))),
        context,
    ) == Dummy(x=2, recursive=Dummy(x=1))

    # Mixed types
    assert replace_context_values(
        {"foo": [ContextValue("$.meta.foo")]},
        context,
    ) == {"foo": ["foo-value"]}
    assert replace_context_values(
        {"foo": Dummy(x=ContextValue("$.meta.a-number"))},
        context,
    ) == {"foo": Dummy(x=1)}
    assert replace_context_values(
        [{"foo": ContextValue("$.meta.foo")}],
        context,
    ) == [{"foo": "foo-value"}]
    assert replace_context_values(
        [Dummy(x=ContextValue("$.meta.a-number"))],
        context,
    ) == [Dummy(x=1)]
    assert replace_context_values(
        Dummy(x=1, list_value=[ContextValue("$.meta.foo")]),
        context,
    ) == Dummy(x=1, list_value=["foo-value"])

    # Large combination
    obj = Dummy(
        x=10,
        list_value=[
            [
                [
                    [
                        ContextValue("$.meta.foo"),
                        "bar",
                    ],
                    "baz",
                ],
            ],
        ],
        dict_value={
            "constant": 123,
            "nested": {
                "list": [
                    1,
                    ContextValue("$.meta.foo"),
                    ContextValue("$.meta.bar"),
                    ["foo", ContextValue("$.meta.foo")],
                    Dummy(x=2),
                    Dummy(x=3, list_value=ContextValue("$.meta.a-list")),
                ],
                "very": {
                    "deeply": {
                        "nested": {
                            "list": [
                                1,
                                ContextValue("$.meta.foo"),
                                ContextValue("$.meta.bar"),
                                ["foo", ContextValue("$.meta.foo")],
                            ],
                        },
                    },
                },
            },
        },
        recursive=Dummy(
            x=4,
            recursive=Dummy(
                x=5,
                recursive=Dummy(
                    x=6,
                    dict_value={
                        "foo": ContextValue("$.meta.foo"),
                    },
                ),
            ),
        ),
    )

    assert replace_context_values(obj, context) == Dummy(
        x=10,
        list_value=[
            [
                [
                    [
                        "foo-value",
                        "bar",
                    ],
                    "baz",
                ],
            ],
        ],
        dict_value={
            "constant": 123,
            "nested": {
                "list": [
                    1,
                    "foo-value",
                    "bar-value",
                    ["foo", "foo-value"],
                    Dummy(x=2),
                    Dummy(x=3, list_value=[1, 2, 3]),
                ],
                "very": {
                    "deeply": {
                        "nested": {
                            "list": [
                                1,
                                "foo-value",
                                "bar-value",
                                ["foo", "foo-value"],
                            ],
                        },
                    },
                },
            },
        },
        recursive=Dummy(
            x=4,
            recursive=Dummy(
                x=5,
                recursive=Dummy(
                    x=6,
                    dict_value={
                        "foo": "foo-value",
                    },
                ),
            ),
        ),
    )


def test_replace_context_values_error(context):
    with pytest.raises(
        ContextValueError,
        match=(
            "failed to process context values: .* for path "
            r"'\$\.meta\.does-not-exist'"
        ),
    ):
        assert replace_context_values(
            ContextValue("$.meta.does-not-exist"),
            context,
        )

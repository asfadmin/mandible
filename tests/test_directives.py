from unittest import mock

import pytest

from mandible.metadata_mapper import Context, FileSource
from mandible.metadata_mapper.builder import _DIRECTIVE_BUILDER_REGISTRY
from mandible.metadata_mapper.directive import (
    DIRECTIVE_REGISTRY,
    Add,
    FloorDiv,
    Mapped,
    Mul,
    Reformatted,
    Sub,
    TrueDiv,
)


def test_all_directives_have_builder_class():
    directive_names = set(DIRECTIVE_REGISTRY)
    builder_names = set(_DIRECTIVE_BUILDER_REGISTRY)

    assert directive_names <= builder_names, \
        "Some directives don't have a builder class!"


def test_mapped_mutually_exclusive_key_options():
    with pytest.raises(ValueError, match="cannot set both"):
        Mapped(
            context=Context(),
            sources={"source": mock.create_autospec(FileSource)},
            source="source",
            key="key",
            key_options={
                "return_list": True,
                "return_first": True,
            },
        )


def test_reformatted_mutually_exclusive_key_options():
    with pytest.raises(ValueError, match="cannot set both"):
        Reformatted(
            context=Context(),
            sources={},
            format="Json",
            value="value",
            key="key",
            key_options={
                "return_list": True,
                "return_first": True,
            },
        )


def test_add():
    add = Add(Context(), {}, 1, 2)

    assert add.call() == 3


def test_floordiv():
    floordiv = FloorDiv(Context(), {}, 1, 2)

    assert floordiv.call() == 0


def test_mul():
    mul = Mul(Context(), {}, 1, 2)

    assert mul.call() == 2


def test_sub():
    sub = Sub(Context(), {}, 1, 2)

    assert sub.call() == -1


def test_truediv():
    truediv = TrueDiv(Context(), {}, 1, 2)

    assert truediv.call() == 0.5

import pytest

from mandible.metadata_mapper.key import Key


def test_resolve_list_match():
    assert Key("foo", return_list=True).resolve_list_match(["a", "b", "c"]) == ["a", "b", "c"]
    assert Key("foo", return_first=True).resolve_list_match(["a", "b", "c"]) == "a"

    with pytest.raises(KeyError):
        Key("foo").resolve_list_match([])

    with pytest.raises(ValueError, match="returned multiple values"):
        Key("foo").resolve_list_match(["a", "b", "c"])


def test_repr():
    assert "default=RAISE_EXCEPTION" in repr(Key("foo"))

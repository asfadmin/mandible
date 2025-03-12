import re
from collections.abc import Generator
from typing import Union

try:
    import jsonpath_ng
    import jsonpath_ng.ext
except ImportError:
    jsonpath_ng = None  # type: ignore


JsonValue = Union[
    # Primitives
    bool,
    float,
    int,
    str,
    # Special constants
    None,
    # Nested structures
    dict[str, "JsonValue"],
    list["JsonValue"],
]

BRACKET_PATTERN = re.compile(r"\[(.*)\]$")


def get(data: JsonValue, path: str) -> list[JsonValue]:
    # Fall back to simple dot paths
    if jsonpath_ng is None:
        return _get_dot_path(data, path)

    expr = jsonpath_ng.ext.parse(path)
    return [match.value for match in expr.find(data)]


def _get_dot_path(data: JsonValue, path: str) -> list[JsonValue]:
    val = data
    for part in _parse_dot_path(path):
        if part == "$":
            continue

        if isinstance(val, dict):
            val = val[part]
        elif isinstance(val, list):
            val = val[int(part)]
        else:
            raise KeyError(path)

    return [val]


def _parse_dot_path(path: str) -> Generator[str]:
    for part in path.split("."):
        if (m := BRACKET_PATTERN.search(part)):
            yield part[:m.start()]
            yield m.group(1)
        else:
            yield part

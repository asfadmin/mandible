from collections.abc import Callable
from typing import Union

from .context import Context

KeyFunc = Callable[[Context], str]
Key = Union[str, KeyFunc]
Template = Union[
    # Primitives
    bool,
    float,
    int,
    str,
    # Special constants
    None,
    # Nested structures
    dict[str, "Template"],
    list["Template"],
    set["Template"],
    tuple["Template", ...],
    # Special types
    KeyFunc,
]

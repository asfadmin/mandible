from collections.abc import Callable
from typing import Union

from .context import Context

KeyFunc = Callable[[Context], str]
Key = Union[str, KeyFunc]
Template = Union[
    dict[str, "Template"],
    list["Template"],
    tuple["Template", ...],
    set["Template"],
    str,
    int,
    float,
    bool,
    KeyFunc,
]

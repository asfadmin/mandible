from typing import Callable, Dict, List, Set, Tuple, Union

from .context import Context

KeyFunc = Callable[[Context], str]
Key = Union[str, KeyFunc]
Template = Union[
    Dict[str, "Template"],
    List["Template"],
    Tuple["Template", ...],
    Set["Template"],
    str,
    int,
    float,
    bool,
    KeyFunc,
]

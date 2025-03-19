from dataclasses import dataclass
from typing import Any, TypeVar, Union

T = TypeVar("T")
RAISE_EXCEPTION = object()


@dataclass(frozen=True)
class Key:
    key: str

    # Optional arguments
    return_list: bool = False
    return_first: bool = False
    default: Any = RAISE_EXCEPTION

    def __post_init__(self) -> None:
        if self.return_list and self.return_first:
            raise ValueError(
                "cannot set both 'return_list' and 'return_first' to True",
            )

    def resolve_list_match(self, values: list[T]) -> Union[list[T], T]:
        if self.return_list:
            return values

        if not values:
            raise KeyError(self.key)

        if not self.return_first and len(values) != 1:
            raise ValueError(
                "returned multiple values (try setting return_list=True)",
            )

        return values[0]

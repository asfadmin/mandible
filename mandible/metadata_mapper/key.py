from dataclasses import dataclass
from typing import Any, List


@dataclass(frozen=True)
class Key:
    key: str

    # Optional arguments
    return_list: bool = False
    return_first: bool = False

    def __post_init__(self):
        if self.return_list and self.return_first:
            raise ValueError(
                "cannot set both 'return_list' and 'return_first' to True",
            )

    def resolve_list_match(self, values: List[Any]) -> Any:
        if self.return_list:
            return values

        if not values:
            raise KeyError(self.key)

        if not self.return_first and len(values) != 1:
            raise ValueError(
                "returned multiple values (try setting return_list=True)",
            )

        return values[0]

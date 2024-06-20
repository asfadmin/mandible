from dataclasses import dataclass
from typing import Any, List


@dataclass(frozen=True)
class Key:
    key: str

    # Optional arguments
    return_list: bool = False

    def resolve_list_match(self, values: List[Any]) -> Any:
        if self.return_list:
            return values

        if not values:
            raise KeyError(self.key)

        if len(values) != 1:
            raise ValueError(
                "returned multiple values (try setting return_list=True)",
            )

        return values[0]

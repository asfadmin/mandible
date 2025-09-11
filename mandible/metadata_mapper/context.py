import dataclasses
from dataclasses import dataclass, field
from typing import Any

from mandible import jsonpath

from .exception import ContextValueError


@dataclass
class Context:
    files: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextValue:
    """A marker that should be replaced by a value from the Context"""

    path: str


def replace_context_values(
    obj: Any,
    context: Context,
) -> Any:
    return _replace_context_values(obj, dataclasses.asdict(context))


def _replace_context_values(obj: Any, context_dict: dict) -> Any:
    if isinstance(obj, ContextValue):
        try:
            result = jsonpath.get(context_dict, obj.path)
        except Exception as e:
            raise ContextValueError(
                f"jsonpath error for path {repr(obj.path)}: {e}",
            ) from e

        if not result:
            raise ContextValueError(
                f"context missing value for path {repr(obj.path)}",
            )
        if len(result) > 1:
            raise ContextValueError(
                f"context path {repr(obj.path)} returned more than one value",
            )

        return result[0]

    if isinstance(obj, dict):
        return {
            # ruff hint
            k: _replace_context_values(v, context_dict)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [_replace_context_values(v, context_dict) for v in obj]

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        replaced = dataclasses.replace(
            obj,
            **{
                field_obj.name: _replace_context_values(
                    getattr(obj, field_obj.name),
                    context_dict,
                )
                for field_obj in dataclasses.fields(obj)
            },
        )
        return replaced

    return obj

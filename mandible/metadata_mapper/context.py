import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List

from mandible import jsonpath


@dataclass
class Context:
    files: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContextValue:
    """A marker that should be replaced by a value from the Context"""
    path: str


def replace_context_values(
    obj: Any,
    context: Context,
    # TODO(reweeden): Implement debug path for exceptions
    debug_path: str = "",
) -> Any:
    return _replace_context_values(obj, dataclasses.asdict(context))


def _replace_context_values(obj: Any, context_dict: dict) -> Any:
    if isinstance(obj, ContextValue):
        result = jsonpath.get(context_dict, obj.path)

        if not result:
            raise KeyError(obj.path)
        if len(result) > 1:
            raise ValueError(
                f"ContextValue path {repr(obj.path)} returned more than "
                f"one value!",
            )

        return result[0]

    if isinstance(obj, dict):
        return {
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

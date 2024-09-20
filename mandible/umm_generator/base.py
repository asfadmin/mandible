import inspect
from typing import Any, Dict, Type


class MISSING:
    __slots__ = ()


class Umm:
    _attributes = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        # TODO(reweeden): Make this work with multiple inheritance?
        parent_cls = super(cls, cls)
        attributes = {**parent_cls._attributes}

        for name, typ in get_annotations(cls).items():
            # TODO(reweeden): What if we're overwriting an attribute from the
            # parent and the types don't match?
            attributes[name] = (typ, getattr(cls, name, MISSING))

        # Update attributes with unannotated default values
        for name, value in inspect.getmembers(cls):
            if name.startswith("_") or inspect.isfunction(value):
                continue

            if name not in attributes:
                attributes[name] = (Any, value)
            else:
                typ, _ = attributes[name]
                attributes[name] = (typ, value)

        cls._attributes = attributes

    def __init__(self, metadata: Dict[str, Any]):
        for name, (typ, default) in self._attributes.items():
            if inspect.isclass(typ) and issubclass(typ, Umm):
                if type(self) is typ:
                    # TODO(reweeden): Error type?
                    raise RuntimeError(
                        f"Self-reference detected for attribute '{name}'",
                    )

                setattr(self, name, typ(metadata))
            else:
                value = default
                if value is MISSING:
                    # TODO(reweeden): Ability to set handler function manually?
                    # For example:
                    # class Foo(Umm):
                    #     Attribute: str = Attr()
                    #
                    #     @Attribute.getter
                    #     def get_attribute(self, metadata):
                    #         ...
                    handler_name = f"get_{name}"
                    handler = getattr(self, handler_name, None)
                    if handler:
                        value = handler(metadata)

                if value is MISSING:
                    # TODO(reweeden): Error type?
                    raise RuntimeError(
                        f"Missing value for '{name}'. "
                        f"Try implementing a 'get_{name}' method",
                    )
                setattr(self, name, value)

    def to_dict(self) -> Dict[str, Any]:
        return _to_dict(self)


def get_annotations(cls) -> Dict[str, Type[Any]]:
    if hasattr(inspect, "get_annotations"):
        return inspect.get_annotations(cls, eval_str=True)

    # TODO(reweeden): String evaluation
    return dict(cls.__annotations__)


def _to_dict(obj: Any) -> Any:
    if isinstance(obj, Umm):
        return {
            name: _to_dict(
                getattr(obj, name),
            )
            for name in obj._attributes
        }

    return obj

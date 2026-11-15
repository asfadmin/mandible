import collections
import datetime
import inspect
from typing import Any, Dict, Optional, Type


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
            attributes[name] = (typ, cls.__dict__.get(name, MISSING))

        # Update attributes with unannotated default values
        for name, value in inspect.getmembers(cls):
            if name.startswith("_") or inspect.isfunction(value):
                continue

            if name not in attributes:
                attributes[name] = (Any, value)

        cls._attributes = attributes

    def __init__(
        self,
        metadata: Dict[str, Any],
        debug_name: Optional[str] = None,
    ):
        if debug_name is None:
            debug_name = self.__class__.__name__
        for name, (typ, default) in self._attributes.items():
            attr_debug_name = f"{debug_name}.{name}"
            try:
                value = self._init_attr_value(
                    name,
                    attr_debug_name,
                    typ,
                    default,
                    metadata,
                )
                setattr(self, name, value)
            except RuntimeError:
                raise
            except Exception as e:
                raise RuntimeError(
                    f"Encountered an error initializing "
                    f"'{attr_debug_name}': {e}",
                ) from e

    def _init_attr_value(
        self,
        attr_name: str,
        debug_name: Optional[str],
        typ: type,
        default: Any,
        metadata: dict,
    ) -> Any:
        if inspect.isclass(typ) and issubclass(typ, Umm):
            if type(self) is typ:
                # TODO(reweeden): Error type?
                raise RuntimeError(
                    f"Self-reference detected for attribute '{debug_name}'",
                )

            return typ(metadata, debug_name=debug_name)

        value = default
        # TODO(reweeden): Ability to set handler function manually?
        # For example:
        # class Foo(Umm):
        #     Attribute: str = Attr()
        #
        #     @Attribute.getter
        #     def get_attribute(self, metadata):
        #         ...
        handler_name = f"get_{attr_name}"
        handler = getattr(self, handler_name, None)

        if value is MISSING:
            if handler is None:
                if (
                    hasattr(typ, "__origin__")
                    and hasattr(typ, "__args__")
                    and issubclass(typ.__origin__, collections.abc.Sequence)
                ):
                    for cls in typ.__args__:
                        if not issubclass(cls, Umm):
                            # TODO(reweeden): Error type?
                            raise RuntimeError(
                                f"Non-Umm element of tuple type found for "
                                f"'{debug_name}'",
                            )
                    return tuple(
                        cls(metadata, debug_name=debug_name)
                        for cls in typ.__args__
                    )

                # TODO(reweeden): Error type?
                raise RuntimeError(
                    f"Missing value for '{debug_name}'. "
                    f"Try implementing a '{handler_name}' method",
                )

            return handler(metadata)
        elif value is not MISSING and handler is not None:
            # TODO(reweeden): Error type?
            raise RuntimeError(
                f"Found both explicit value and handler function for "
                f"'{debug_name}'",
            )

        return value

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
            name: _to_dict(value)
            for name in obj._attributes
            # Filter out optional keys, marked by having a `None` value
            if (value := getattr(obj, name)) is not None
        }

    if isinstance(obj, collections.abc.Sequence) and not isinstance(obj, str):
        return [_to_dict(item) for item in obj]

    # TODO(reweeden): Serialize to string here, or do that via JSON encoder?
    if isinstance(obj, datetime.datetime):
        return obj

    return obj

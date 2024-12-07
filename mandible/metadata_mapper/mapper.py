import inspect
import logging
from typing import Any, Optional

from .context import Context
from .directive import DIRECTIVE_REGISTRY, TemplateDirective
from .exception import MetadataMapperError, TemplateError
from .source import Source, SourceProvider
from .types import Template

log = logging.getLogger(__name__)


class MetadataMapper:
    def __init__(
        self,
        template: Template,
        source_provider: SourceProvider = None,
        *,
        directive_marker: str = "@",
    ):
        self.template = template
        self.source_provider = source_provider
        self.directive_marker = directive_marker

    def get_metadata(self, context: Context) -> Template:
        if self.source_provider is not None:
            sources = self.source_provider.get_sources()
        else:
            sources = {}

        try:
            self._cache_source_keys(context, sources)
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to cache source keys: {e}"
            ) from e

        for name, source in sources.items():
            log.info("Querying source %r: %s", name, source)
            try:
                source.query_all_values(context)
            except Exception as e:
                raise MetadataMapperError(
                    f"failed to query source {repr(name)}: {e}",
                ) from e

        try:
            return self._replace_template(context, self.template, sources)
        except TemplateError:
            raise
        except Exception as e:
            raise MetadataMapperError(
                f"failed to evaluate template: {e}"
            ) from e

    def _cache_source_keys(self, context: Context, sources: dict[str, Source]):
        for value, debug_path in _walk_values(self.template):
            if isinstance(value, dict):
                directive_name = self._get_directive_name(value, debug_path)
                if directive_name is None:
                    continue

                directive = self._get_directive(
                    directive_name,
                    context,
                    sources,
                    value[directive_name],
                    f"{debug_path}.{directive_name}",
                )
                directive.prepare()

    def _replace_template(
        self,
        context: Context,
        template: Template,
        sources: dict[str, Source],
        debug_path: str = "$",
    ):
        if isinstance(template, dict):
            directive_name = self._get_directive_name(
                template,
                debug_path
            )
            if directive_name is not None:
                debug_path = f"{debug_path}.{directive_name}"
                directive = self._get_directive(
                    directive_name,
                    context,
                    sources,
                    {
                        k: self._replace_template(
                            context,
                            v,
                            sources,
                            debug_path=f"{debug_path}.{k}",
                        )
                        for k, v in template[directive_name].items()
                    },
                    debug_path
                )
                try:
                    return directive.call()
                except Exception as e:
                    raise MetadataMapperError(
                        f"failed to call directive at {debug_path}: {e}"
                    ) from e

            return {
                k: self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}.{k}",
                )
                for k, v in template.items()
            }

        if isinstance(template, list):
            return [
                self._replace_template(
                    context,
                    v,
                    sources,
                    debug_path=f"{debug_path}[{i}]",
                )
                for i, v in enumerate(template)
            ]

        return template

    def _get_directive_name(
        self,
        value: dict,
        debug_path: str,
    ) -> Optional[str]:
        directive_names = [
            key for key in value
            if key.startswith(self.directive_marker)
        ]
        if not directive_names:
            return None

        if len(directive_names) > 1:
            raise TemplateError(
                "multiple directives found in config: "
                f"{', '.join(repr(d) for d in directive_names)}",
                debug_path
            )

        return directive_names[0]

    def _get_directive(
        self,
        directive_name: str,
        context: Context,
        sources: dict[str, Source],
        config: dict,
        debug_path: str,
    ) -> TemplateDirective:
        cls = DIRECTIVE_REGISTRY.get(directive_name[len(self.directive_marker):])
        if cls is None:
            raise TemplateError(
                f"invalid directive {repr(directive_name)}",
                debug_path
            )

        argspec = inspect.getfullargspec(cls.__init__)

        # Ignore the `self`, `context`, and `sources` parameters
        required_keys = set(
            argspec.args[3:-len(argspec.defaults)]
            if argspec.defaults else
            argspec.args[3:]
        )
        config_keys = set(config.keys())
        diff = required_keys - config_keys

        if diff:
            s = ""
            if len(diff) > 1:
                s = "s"
            raise TemplateError(
                f"missing key{s}: "
                f"{', '.join(repr(d) for d in sorted(diff))}",
                debug_path
            )

        # For forward compatibility, ignore any unexpected keys
        all_keys = set(argspec.args[2:])
        kwargs = {
            k: v
            for k, v in config.items()
            if k in all_keys
        }

        try:
            return cls(context, sources, **kwargs)
        except Exception as e:
            raise TemplateError(str(e), debug_path) from e


def _walk_values(obj: Any, debug_path: str = "$"):
    yield obj, debug_path
    if isinstance(obj, dict):
        for key, val in obj.items():
            yield from _walk_values(val, f"{debug_path}.{key}")
    elif isinstance(obj, (list, tuple, set)):
        for i, val in enumerate(obj):
            yield from _walk_values(val, f"{debug_path}[{i}]")

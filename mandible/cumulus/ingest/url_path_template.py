# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/ingest/src/url-path-template.js

import re

from mandible.jsonpath import get

TEMPLATE_PATTERN = re.compile("{([^{}]+)}")
EXPRESSION_PATTERN = re.compile(r"([^(]+)\(([^)]+)\)")


def _get_single_value(data: dict, path: str):
    values = get(data, path)

    if not values:
        raise Exception(f"Could not resolve path {repr(path)}")

    if len(values) != 1:
        raise ValueError(f"Path returned multiple values {repr(path)}")

    return values[0]


def evaluate_operation(name, args):
    """evaluate the operation specified in template

    :param name: the name of the operation
    :param args: the args (in array) of the operation
    :returns: str - the return value of the operation
    """
    raise NotImplementedError("evaluate_operation is not implemented yet")


def template_replacer(context: dict, match: re.Match) -> str:
    """retrieve the actual value of the matched string and return it

    :param context: the metadata used in the template
    :param match: the match object from re.sub
    :returns: str - the value of the matched string
    """
    submatch = match.group(1)
    m = EXPRESSION_PATTERN.search(submatch)

    if m:
        raise NotImplementedError("operations are not implemented yet")

    return _get_single_value(context, submatch)


def url_path_template(path_template: str, context: dict) -> str:
    """define the path of a file based on the metadata of a granule

    :param path_template: the template that defines the path, using `{}` for
        string interpolation
    :param context: the metadata used in the template
    :returns: str - the url path for the file
    """
    try:
        replaced_path = TEMPLATE_PATTERN.sub(
            lambda m: template_replacer(context, m),
            path_template,
        )
        if TEMPLATE_PATTERN.search(replaced_path):
            return url_path_template(replaced_path, context)
        return replaced_path
    except Exception as e:
        raise Exception(
            f"Could not resolve path template {repr(path_template)} with error "
            f"{repr(str(e))}",
        ) from e

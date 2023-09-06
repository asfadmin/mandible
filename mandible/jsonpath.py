try:
    import jsonpath_ng
    import jsonpath_ng.ext
except ImportError:
    jsonpath_ng = None


def get_key(data: dict, key: str):
    # Fall back to simple dot paths
    if jsonpath_ng is None:
        val = data
        for key in key.split("."):
            val = val[key]

        return val

    expr = jsonpath_ng.ext.parse(key)
    # TODO(reweeden): Add a way to return the whole list here and not just
    # the first element.
    try:
        return next(match.value for match in expr.find(data))
    except StopIteration:
        raise KeyError(key)

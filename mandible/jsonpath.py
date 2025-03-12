try:
    import jsonpath_ng
    import jsonpath_ng.ext
except ImportError:
    jsonpath_ng = None  # type: ignore


def get(data: dict, path: str) -> list:
    # Fall back to simple dot paths
    if jsonpath_ng is None:
        val = data
        for part in path.split("."):
            if part == "$":
                continue

            val = val[part]

        return [val]

    expr = jsonpath_ng.ext.parse(path)
    return [match.value for match in expr.find(data)]

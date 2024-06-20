from mandible.metadata_mapper.key import Key

try:
    import jsonpath_ng
    import jsonpath_ng.ext
except ImportError:
    jsonpath_ng = None


def get_key(data: dict, key: Key):
    # Fall back to simple dot paths
    if jsonpath_ng is None:
        if key.key == "$":
            return data

        val = data
        for part in key.key.split("."):
            val = val[part]

        return val

    expr = jsonpath_ng.ext.parse(key.key)
    values = [match.value for match in expr.find(data)]

    return key.resolve_list_match(values)

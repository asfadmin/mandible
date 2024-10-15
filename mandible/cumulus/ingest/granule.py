# Ported from:
# https://github.com/nasa/cumulus/blob/master/packages/ingest/src/granule.ts

import re

SUFFIX_PATTERN = re.compile(
    r"\.v[0-9]{4}(0[1-9]|1[0-2])(0[1-9]|[1-2][0-9]|3[0-1])T(2[0-3]|[01][0-9])"
    r"[0-5][0-9][0-5][0-9][0-9]{3}$",
)


def is_file_renamed(filename: str) -> bool:
    """check to see if the file has the suffix with timestamp
    '.vYYYYMMDDTHHmmssSSS'

    :param filename: name of the file
    :returns: bool - whether the file is renamed
    """
    return SUFFIX_PATTERN.search(filename) is not None


def unversion_filename(filename: str) -> str:
    """Returns the input filename stripping off any versioned timestamp.

    :param filename:
    :returns: str - filename with timestamp removed
    """
    if is_file_renamed(filename):
        return ".".join(filename.split(".")[0:-1])

    return filename

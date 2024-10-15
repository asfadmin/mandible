# Ported from:
# https://github.com/nasa/cumulus/blob/master/tasks/move-granules/index.js

import re
from pathlib import Path
from typing import List, Tuple

from mandible.cumulus.ingest.granule import unversion_filename
from mandible.cumulus.ingest.url_path_template import url_path_template


def validate_match(
    match: List[dict],
    buckets_config: dict,
    file_name: str,
    file_specs: List[dict],
):
    """Validates the file matched only one collection.file and has a valid
    bucket config.

    :param match: list of matched collection.file.
    :param buckets_config: BucketsConfig instance describing stack configuration.
    :param file_name: the file name tested.
    :param file_specs: array of collection file specifications objects.
    :raises: ValueError - If match is invalid, throws an error.
    """
    collection_regexes = [spec["regex"] for spec in file_specs]
    if len(match) > 1:
        raise ValueError(
            f"File ({file_name}) matched more than one of "
            f"{collection_regexes}.",
        )
    if not match:
        raise ValueError(
            f"File ({file_name}) did not match any of {collection_regexes}",
        )

    bucket = match[0]["bucket"]
    if bucket not in buckets_config:
        raise ValueError(
            f"Collection config specifies a bucket key of {repr(bucket)}, but "
            f"the configured bucket keys are: "
            f"{', '.join(repr(bucket) for bucket in buckets_config.keys())}",
        )


def get_bucket_and_key_for_file(
    file: dict,
    granule: dict,
    collection: dict,
    cmr_metadata: dict,
    buckets_config: dict,
) -> Tuple[str, str]:
    """Get the bucket and key that MoveGranules will move a file to.

    NOTE: This does not exist as a function in cumulus move-granules. It is
    extracted from the following lines for reuse in our code:
    https://github.com/nasa/cumulus/blob/5342484a6f1836bfb5ac6a4523b4069c17cd74e0/tasks/move-granules/index.js#L108-L118

    :param file: a file entry from the granule object to match
    :param granule: a single entry from a cumulus granules list
    :param collection: configuration object defining a collection of granules
        and their files
    :param cmr_metadata: the UMM-G record associated with this granule
    :param buckets_config: BucketsConfig instance associated with the stack
    :returns: str, str - bucket name and key where the file will be moved
    """
    file_specs = collection["files"]
    file_name = Path(file["key"]).name

    match = [
        file
        for file in file_specs
        # NOTE: We ignore any differences in regex syntax between javascript
        # and python. This could cause certain regexes to break or match
        # incorrectly.
        if re.search(file["regex"], unversion_filename(file_name))
    ]
    validate_match(match, buckets_config, file_name, file_specs)
    file_spec = match[0]

    url_path_template_string = (
        file_spec.get("url_path")
        or collection.get("url_path")
        or ""
    )
    url_path = url_path_template(
        url_path_template_string,
        {
            "file": file,
            "granule": granule,
            "cmrMetadata": cmr_metadata,
        },
    )
    bucket_name = buckets_config[file_spec["bucket"]]["name"]
    updated_key = url_path + file_name

    return bucket_name, updated_key

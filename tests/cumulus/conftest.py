import pytest


@pytest.fixture
def buckets_config() -> dict:
    return {
        "browse": {
            "name": "stack-cumulus-dev-browse",
            "type": "public",
        },
        "private": {
            "name": "stack-cumulus-dev-private",
            "type": "private",
        },
        "protected": {
            "name": "stack-cumulus-dev-protected",
            "type": "protected",
        },
        "staging": {
            "name": "stack-cumulus-dev-staging",
            "type": "workflow",
        },
    }


@pytest.fixture
def collection() -> dict:
    return {
        "createdAt": 1711567923110,
        "updatedAt": 1728584062910,
        "name": "SAMPLE-COLLECTION",
        "version": "1",
        "process": "rtc",
        "url_path": "default/{granule.granuleId}/",
        "duplicateHandling": "replace",
        "granuleId": "^SAMPLE.*$",
        "granuleIdExtraction": "(SAMPLE.*)(\\.nc)",
        "files": [
            {
                "regex": "^SAMPLE_.*\\.(?:nc|iso\\.xml|)(?!png)(?:\\.md5)?$",
                "bucket": "protected",
                "sampleFileName": "SAMPLE_000000.nc",
                "url_path": "products/{granule.granuleId}/",
            },
            {
                "regex": "^SAMPLE_.*\\.(?!nc|iso\\.xml)(?:png)(?:\\.md5)?$",
                "bucket": "browse",
                "sampleFileName": "SAMPLE_000000.png",
            },
        ],
        "sampleFileName": "SAMPLE_000000.nc",
    }

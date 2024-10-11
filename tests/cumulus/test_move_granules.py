import pytest

from mandible.cumulus.move_granules import get_bucket_and_key_for_file


@pytest.fixture
def granule():
    return {
        "granuleId": "SAMPLE_123456",
        "dataType": "SAMPLE-COLLECTION",
        "version": "1",
        "provider": "SAMPLE-PROVIDER",
        "files": [
            {
                "size": 651707,
                "bucket": "stack-cumulus-dev-staging",
                "key": "SAMPLE_123456/stack-cumulus-dev/SAMPLE-COLLECTION___1/SAMPLE_123456.iso.xml",
                "source": "SAMPLE-COLLECTION/1/SAMPLE_123456/SAMPLE_123456.iso.xml",
                "fileName": "SAMPLE_123456.iso.xml",
                "type": "metadata",
                "checksumType": "md5",
                "checksum": "02eabbbfda193330567bc5b978f8b4a0",
            },
            {
                "size": 32,
                "bucket": "stack-cumulus-dev-staging",
                "key": "SAMPLE_123456/stack-cumulus-dev/SAMPLE-COLLECTION___1/SAMPLE_123456.iso.xml.md5",
                "source": "SAMPLE-COLLECTION/1/SAMPLE_123456/SAMPLE_123456.iso.xml.md5",
                "fileName": "SAMPLE_123456.iso.xml.md5",
                "type": "metadata",
                "checksumType": "md5",
                "checksum": "b7edf8ceb761b7e7800fb6f98451fcb7",
            },
            {
                "size": 322961408,
                "bucket": "stack-cumulus-dev-staging",
                "key": "SAMPLE_123456/stack-cumulus-dev/SAMPLE-COLLECTION___1/SAMPLE_123456.nc",
                "source": "SAMPLE-COLLECTION/1/SAMPLE_123456/SAMPLE_123456.nc",
                "fileName": "SAMPLE_123456.nc",
                "type": "data",
                "checksumType": "md5",
                "checksum": "36a0ad006f5bc0f20f0c3df795f9ed02",
            },
            {
                "size": 32,
                "bucket": "stack-cumulus-dev-staging",
                "key": "SAMPLE_123456/stack-cumulus-dev/SAMPLE-COLLECTION___1/SAMPLE_123456.nc.md5",
                "source": "SAMPLE-COLLECTION/1/SAMPLE_123456/SAMPLE_123456.nc.md5",
                "fileName": "SAMPLE_123456.nc.md5",
                "type": "metadata",
                "checksumType": "md5",
                "checksum": "5883ac4f0bfe308128bad94db6aaf146",
            },
        ],
        "sync_granule_duration": 14204,
        "createdAt": 1728584239122,
    }


def test_get_bucket_and_key_for_file(granule, collection, buckets_config):
    file = [
        file
        for file in granule["files"]
        if file["fileName"].endswith(".nc")
    ][0]
    assert get_bucket_and_key_for_file(
        file,
        granule,
        collection,
        {},
        buckets_config,
    ) == ("stack-cumulus-dev-protected", "products/SAMPLE_123456/SAMPLE_123456.nc")


def test_get_bucket_and_key_for_file_invalid_collection(
    granule,
    collection,
    buckets_config,
):
    # Add a duplicate file entry to the collection
    collection["files"].append(collection["files"][0])

    file = [
        file
        for file in granule["files"]
        if file["fileName"].endswith(".nc")
    ][0]
    with pytest.raises(ValueError, match="matched more than one of"):
        get_bucket_and_key_for_file(
            file,
            granule,
            collection,
            {},
            buckets_config,
        )


def test_get_bucket_and_key_for_file_invalid_collection_bucket(
    granule,
    collection,
    buckets_config,
):
    collection["files"][0]["bucket"] = "does-not-exist"

    file = [
        file
        for file in granule["files"]
        if file["fileName"].endswith(".nc")
    ][0]
    with pytest.raises(
        ValueError,
        match=(
            "specifies a bucket key of 'does-not-exist', but the configured "
            "bucket keys are"
        ),
    ):
        get_bucket_and_key_for_file(
            file,
            granule,
            collection,
            {},
            buckets_config,
        )


def test_get_bucket_and_key_for_file_missing_file(
    granule,
    collection,
    buckets_config,
):
    file = {
        "size": 12345,
        "bucket": "stack-cumulus-dev-staging",
        "key": "SAMPLE_123456/stack-cumulus-dev/SAMPLE-COLLECTION___1/SAMPLE_123456.foobar",
        "source": "SAMPLE-COLLECTION/1/SAMPLE_123456/SAMPLE_123456.foobar",
        "fileName": "SAMPLE_123456.foobar",
        "type": "metadata",
        "checksumType": "md5",
        "checksum": "00000000000000000000000000000000",
    }
    with pytest.raises(ValueError, match="did not match any of"):
        get_bucket_and_key_for_file(
            file,
            granule,
            collection,
            {},
            buckets_config,
        )

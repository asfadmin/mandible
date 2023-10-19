from datetime import datetime, timezone
from typing import List, Optional

import pytest
from freezegun import freeze_time

from mandible.umm.ummg import UmmgBase
from mandible.umm.ummg_types import AdditionalAttribute, Metadata, PgeVersion


@freeze_time("2022-08-25 21:45:44.123456")
def test_ummg():
    data = {
        "collection_info": {
            "short_name": "test-short-name",
            "long_name": "test-long-name"
        },
        "product_md": {
            "product_creation_datetime": datetime.now(timezone.utc),
            "product_start_time": datetime.now(timezone.utc),
            "product_stop_time": datetime.now(timezone.utc),
            "mission": "tester-mission-9000"
        },
        "product_files_md": {
            "product_file":  {
                "name": "test.xml",
                "uri": "http://test/test.xml",
                "s3uri": "s3://test/test.xml",
                "size": 123456,
                "key": "test.xml",
                "bucket": "test",
            },
            "related_files": [
                {
                    "name": "test.xml.md5",
                    "uri": "http://test/test.xml.md5",
                    "s3uri": "s3://test/test.xml.md5",
                    "size": 123,
                    "key": "test.xml.md5",
                    "bucket": "test",
                }
            ]
        }
    }
    ummg_data = UmmgBase(data)
    res = ummg_data.get_ummg()
    assert res == {
        "CollectionReference": {"EntryTitle": "test-long-name"},
        "DataGranule": {
            "ArchiveAndDistributionInformation": [{
                "Format": "XML",
                "Name": "test.xml",
                "SizeInBytes": 123456
            }],
            "DayNightFlag": "Unspecified",
            "Identifiers": [{
                "Identifier": "test",
                "IdentifierType": "ProducerGranuleId"
            }],
            "ProductionDateTime": "2022-08-25T21:45:44.123456Z"
        },
        "GranuleUR": "test-xml",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.4",
            "Version": "1.6.4"
        },
        "Platforms": [{"ShortName": "tester-mission-9000"}],
        "ProviderDates": [
            {
                "Date": "2022-08-25T21:45:44.123456Z",
                "Type": "Insert"
            },
            {
                "Date": "2022-08-25T21:45:44.123456Z",
                "Type": "Update"
            }
        ],
        "RelatedUrls": [
            {
                "Subtype": "VERTEX",
                "Type": "GET DATA",
                "URL": "http://test/test.xml"
            },
            {
                "Type": "GET DATA VIA DIRECT ACCESS",
                "URL": "s3://test/test.xml"
            }
        ],
        "TemporalExtent": {
            "RangeDateTime": {
                "BeginningDateTime": "2022-08-25T21:45:44.123456Z",
                "EndingDateTime": "2022-08-25T21:45:44.123456Z"
            }
        },
    }


@freeze_time("2022-08-25 21:45:44.123456")
def test_custom_ummg():
    class AdditionalAttributeUmmg(UmmgBase):
        def get_additional_attributes(self) -> Optional[List[AdditionalAttribute]]:
            return self.product_metadata["additional_attributes"]

        def get_pge_version(self) -> Optional[PgeVersion]:
            return self.product_metadata["pge_version"]

    data: Metadata = {
        "collection_info": {
            "short_name": "test-json-short-name",
            "long_name": "test-json-long-name"
        },
        "product_md": {
            "product_creation_datetime": datetime.now(timezone.utc),
            "product_start_time": datetime.now(timezone.utc),
            "product_stop_time": datetime.now(timezone.utc),
            "mission": "tester-mission-9000",
            "optional": {
                "additional_attributes": [
                    {
                        "Name": "test",
                        "Value": "1"
                    },
                ],
                "pge_version": {"PGEVersion": "test-version-1"}
            }
        },
        "product_files_md": {
            "product_file":  {
                "name": "test.json",
                "uri": "http://test/test.json",
                "s3uri": "s3://test/test.json",
                "size": 123456,
            },
            "related_files": [
                {
                    "name": "test.json.md5",
                    "uri": "http://test/test.json.md5",
                    "s3uri": "s3://test/test.json.md5",
                    "size": 123,
                }
            ]
        }
    }
    ummg_data = AdditionalAttributeUmmg(data)
    res = ummg_data.get_ummg()
    assert res == {
        "AdditionalAttributes": [
            {
                "Name": "test",
                "Value": "1"
            }
        ],
        "CollectionReference": {
            "EntryTitle": "test-json-long-name"
        },
        "DataGranule": {
            "ArchiveAndDistributionInformation": [
                {
                    "Format": "JSON",
                    "Name": "test.json",
                    "SizeInBytes": 123456
                }
            ],
            "DayNightFlag": "Unspecified",
            "Identifiers": [
                {
                    "Identifier": "test",
                    "IdentifierType": "ProducerGranuleId"
                }
            ],
            "ProductionDateTime": "2022-08-25T21:45:44.123456Z"
        },
        "GranuleUR": "test-json",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.4",
            "Version": "1.6.4"
        },
        "PGEVersionClass": {
            "PGEVersion": "test-version-1"
        },
        "Platforms": [
            {
                "ShortName": "tester-mission-9000"
            }
        ],
        "ProviderDates": [
            {
                "Date": "2022-08-25T21:45:44.123456Z",
                "Type": "Insert"
            },
            {
                "Date": "2022-08-25T21:45:44.123456Z",
                "Type": "Update"
            }
        ],
        "RelatedUrls": [
            {
                "Subtype": "VERTEX",
                "Type": "GET DATA",
                "URL": "http://test/test.json"
            },
            {
                "Type": "GET DATA VIA DIRECT ACCESS",
                "URL": "s3://test/test.json"
            }
        ],
        "TemporalExtent": {
            "RangeDateTime": {
                "BeginningDateTime": "2022-08-25T21:45:44.123456Z",
                "EndingDateTime": "2022-08-25T21:45:44.123456Z"
            }
        },
    }


def test_missing_keys():
    data: Metadata = {
        "collection_info": {
            "short_name": "test-short-name",
            "long_name": "test-long-name"
        },
        "product_md": {
            "product_creation_datetime": datetime.now(timezone.utc)
        },
        "product_files_md": {
            "product_file":  {
                "name": "test.xml",
                "uri": "http://test/test.xml",
                "s3uri": "s3://test/test.xml",
                "size": 123456,
            },
            "related_files": [
                {
                    "name": "test.xml.md5",
                    "uri": "http://test/test.xml.md5",
                    "s3uri": "s3://test/test.xml.md5",
                    "size": 123,
                }
            ]
        }
    }
    with pytest.raises(KeyError, match="mission"):
        UmmgBase(data).get_ummg()

    with pytest.raises(KeyError, match="product_md"):
        UmmgBase({})

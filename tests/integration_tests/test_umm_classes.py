import datetime
from typing import Optional

import pytest

from mandible.umm_classes import (
    RelatedUrlBuilder,
    TeaUrlBuilder,
    UmmgBase,
    UmmgCollectionReferenceShortNameVersionMixin,
    UmmgDataGranuleProducerGranuleIdMixin,
    UmmgPlatformMixin,
    UmmgTemporalExtentRangeDateTimeMixin,
)
from mandible.umm_classes.factory import (
    additional_attribute,
    identifier,
    pge_version_class,
)
from mandible.umm_classes.types import (
    AccessConstraints,
    AdditionalAttribute,
    ArchiveAndDistributionInformation,
    CMAGranule,
    CMAGranuleFile,
    Identifier,
    Instrument,
    MeasuredParameter,
    OrbitCalculatedSpatialDomain,
    PGEVersionClass,
    Project,
    SpatialExtent,
    TilingIdentificationSystem,
)


class LocalUmmgBase(UmmgCollectionReferenceShortNameVersionMixin, UmmgBase):
    def get_cmr_short_name(self) -> str:
        return "TEST_CMR_SHORT_NAME"

    def get_cmr_version(self) -> str:
        return "1"


@pytest.fixture
def granule() -> CMAGranule:
    return {
        "granuleId": "TEST_GRANULE_ID",
        "files": [
            {
                "fileName": "test_file.txt",
                "bucket": "test_bucket",
                "key": "test_prefix/test_file.txt",
                "type": "data",
            },
        ],
    }


def test_get_ummg_basic(granule):
    ummg_obj = LocalUmmgBase(granule)
    ummg_obj.now = datetime.datetime(2025, 1, 1)

    ummg_dict = ummg_obj.get_ummg()

    assert ummg_dict == {
        "CollectionReference": {
            "ShortName": "TEST_CMR_SHORT_NAME",
            "Version": "1",
        },
        "GranuleUR": "TEST_GRANULE_ID",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5",
            "Version": "1.6.5",
        },
        "ProviderDates": [
            {"Date": "2025-01-01T00:00:00Z", "Type": "Insert"},
            {"Date": "2025-01-01T00:00:00Z", "Type": "Update"},
        ],
    }


def test_get_ummg_full(granule):
    class FullUmmg(
        UmmgDataGranuleProducerGranuleIdMixin,
        UmmgPlatformMixin,
        UmmgTemporalExtentRangeDateTimeMixin,
        LocalUmmgBase,
    ):
        def get_access_constraints(self) -> AccessConstraints:
            return {
                "Value": 1,
            }

        def get_additional_attributes(self) -> list[AdditionalAttribute]:
            # Return the attributes out of order so they get sorted
            return super().get_additional_attributes() + [
                additional_attribute("TEST_ADDITIONAL_ATTRIBUTE_2", "TEST_VALUE_2"),
                additional_attribute("TEST_ADDITIONAL_ATTRIBUTE", "TEST_VALUE"),
            ]

        def get_archive_and_distribution_information(
            self,
        ) -> list[ArchiveAndDistributionInformation]:
            return super().get_archive_and_distribution_information() + [
                {
                    "Name": "distribution.zip",
                    "Size": 0.5,
                    "SizeUnit": "MB",
                    "Format": "Zip",
                    "MimeType": "application/zip",
                    "Checksum": {
                        "Value": "00000000000000000000000000000000",
                        "Algorithm": "MD5",
                    },
                    "Files": [
                        {
                            "Name": file["fileName"],
                            "SizeInBytes": 12345,
                            "Format": "Text",
                            "FormatType": "NA",
                            "Checksum": {
                                "Value": "00000000000000000000000000000000",
                                "Algorithm": "MD5",
                            },
                        }
                        for file in self.granule["files"]
                    ],
                },
            ]

        def get_beginning_date_time(self) -> datetime.datetime:
            return datetime.datetime(2024, 1, 1)

        def get_cloud_cover(self) -> int:
            return 0

        def get_ending_date_time(self) -> datetime.datetime:
            return datetime.datetime(2024, 1, 2)

        def get_grid_mapping_names(self) -> list[str]:
            return super().get_grid_mapping_names() + [
                "GRID_MAPPING_NAME_1",
                "GRID_MAPPING_NAME_2",
            ]

        def get_identifiers(self) -> list[Identifier]:
            return super().get_identifiers() + [
                identifier("Other", "TEST_SAS_VERSION", "SASVersionId"),
            ]

        def get_input_granules(self) -> list[str]:
            return super().get_input_granules() + [
                "INPUT_GRANULE_1",
                "INPUT_GRANULE_2",
            ]

        def get_instruments(self) -> list[Instrument]:
            return super().get_instruments() + [
                {
                    "ShortName": "INSTRUMENT_1",
                    "Characteristics": [
                        {
                            "Name": "CHARACTERISTIC_1",
                            "Value": "VALUE_1",
                        },
                    ],
                    "ComposedOf": [
                        {"ShortName": "INSTRUMENT_1-A"},
                        {"ShortName": "INSTRUMENT_1-B"},
                    ],
                    "OperationalModes": ["OP1", "OP2"],
                },
            ]

        def get_measured_parameters(self) -> list[MeasuredParameter]:
            return super().get_measured_parameters() + [
                {
                    "ParameterName": "PARAM_1",
                },
                {
                    "ParameterName": "PARAM_2",
                    "QAStats": {},
                    "QAFlags": {},
                },
            ]

        def get_native_projection_names(self) -> list[str]:
            return super().get_native_projection_names() + [
                "NATIVE_PROJECTION_NAME_1",
                "NATIVE_PROJECTION_NAME_2",
            ]

        def get_orbit_calculated_spatial_domains(
            self,
        ) -> list[OrbitCalculatedSpatialDomain]:
            return super().get_orbit_calculated_spatial_domains() + [
                {
                    "OrbitNumber": 1234,
                },
            ]

        def get_pge_version_class(self) -> PGEVersionClass:
            return pge_version_class("TEST_PGE_NAME", "1.1.1.1")

        def get_platform_name(self) -> str:
            return "PLATFORM_NAME"

        def get_producer_granule_id(self) -> str:
            return self.get_granule_ur()

        def get_production_date_time(self) -> datetime.datetime:
            return datetime.datetime(2025, 1, 2)

        def get_projects(self) -> list[Project]:
            return super().get_projects() + [
                {
                    "ShortName": "PROJECT_1",
                    "Campaigns": ["CAMPAIGN_1", "CAMPAIGN_1"],
                },
            ]

        def get_related_url_builder(
            self,
            file: CMAGranuleFile,
        ) -> Optional[RelatedUrlBuilder]:
            bucket = file["bucket"]

            if bucket.endswith("test_bucket"):
                return TeaUrlBuilder(
                    file,
                    "https://example-distribution.123",
                    "TEST/PATH",
                )

            return None

        def get_reprocessing_actual(self) -> str:
            return "TEST_REPROCESSING_ACTUAL"

        def get_reprocessing_planned(self) -> str:
            return "TEST_REPROCESSING_PLANNED"

        def get_spatial_extent(self) -> SpatialExtent:
            points = [(1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (7.0, 8.0)]
            return {
                "HorizontalSpatialDomain": {
                    "Geometry": {
                        "GPolygons": [
                            {
                                "Boundary": {
                                    "Points": [
                                        {
                                            "Latitude": lat,
                                            "Longitude": lon,
                                        }
                                        for lat, lon in points
                                    ],
                                },
                            },
                        ],
                    },
                },
            }

        def get_tiling_identification_system(self) -> TilingIdentificationSystem:
            return {
                "TilingIdentificationSystemName": "TILING_IDENTIFICATION_SYSTEM_1",
                "Coordinate1": {},
                "Coordinate2": {},
            }

    ummg_obj = FullUmmg(granule)
    ummg_obj.now = datetime.datetime(2025, 1, 1)

    ummg_dict = ummg_obj.get_ummg()

    assert ummg_dict == {
        "AccessConstraints": {
            "Value": 1,
        },
        "AdditionalAttributes": [
            {
                "Name": "TEST_ADDITIONAL_ATTRIBUTE",
                "Values": ["TEST_VALUE"],
            },
            {
                "Name": "TEST_ADDITIONAL_ATTRIBUTE_2",
                "Values": ["TEST_VALUE_2"],
            },
        ],
        "CloudCover": 0,
        "CollectionReference": {
            "ShortName": "TEST_CMR_SHORT_NAME",
            "Version": "1",
        },
        "DataGranule": {
            "ArchiveAndDistributionInformation": [
                {
                    "Name": "distribution.zip",
                    "Size": 0.5,
                    "SizeUnit": "MB",
                    "Format": "Zip",
                    "MimeType": "application/zip",
                    "Checksum": {
                        "Value": "00000000000000000000000000000000",
                        "Algorithm": "MD5",
                    },
                    "Files": [
                        {
                            "Name": "test_file.txt",
                            "SizeInBytes": 12345,
                            "Format": "Text",
                            "FormatType": "NA",
                            "Checksum": {
                                "Value": "00000000000000000000000000000000",
                                "Algorithm": "MD5",
                            },
                        },
                    ],
                },
            ],
            "DayNightFlag": "Unspecified",
            "Identifiers": [
                {
                    "IdentifierType": "ProducerGranuleId",
                    "Identifier": "TEST_GRANULE_ID",
                },
                {
                    "IdentifierType": "Other",
                    "IdentifierName": "SASVersionId",
                    "Identifier": "TEST_SAS_VERSION",
                },
            ],
            "ProductionDateTime": "2025-01-02T00:00:00Z",
            "ReprocessingActual": "TEST_REPROCESSING_ACTUAL",
            "ReprocessingPlanned": "TEST_REPROCESSING_PLANNED",
        },
        "GranuleUR": "TEST_GRANULE_ID",
        "GridMappingNames": ["GRID_MAPPING_NAME_1", "GRID_MAPPING_NAME_2"],
        "InputGranules": ["INPUT_GRANULE_1", "INPUT_GRANULE_2"],
        "MeasuredParameters": [
            {
                "ParameterName": "PARAM_1",
            },
            {
                "ParameterName": "PARAM_2",
                "QAStats": {},
                "QAFlags": {},
            },
        ],
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5",
            "Version": "1.6.5",
        },
        "NativeProjectionNames": [
            "NATIVE_PROJECTION_NAME_1",
            "NATIVE_PROJECTION_NAME_2",
        ],
        "OrbitCalculatedSpatialDomains": [
            {
                "OrbitNumber": 1234,
            },
        ],
        "PGEVersionClass": {
            "PGEName": "TEST_PGE_NAME",
            "PGEVersion": "1.1.1.1",
        },
        "Platforms": [
            {
                "ShortName": "PLATFORM_NAME",
                "Instruments": [
                    {
                        "ShortName": "INSTRUMENT_1",
                        "Characteristics": [
                            {
                                "Name": "CHARACTERISTIC_1",
                                "Value": "VALUE_1",
                            },
                        ],
                        "ComposedOf": [
                            {"ShortName": "INSTRUMENT_1-A"},
                            {"ShortName": "INSTRUMENT_1-B"},
                        ],
                        "OperationalModes": ["OP1", "OP2"],
                    },
                ],
            },
        ],
        "Projects": [
            {
                "ShortName": "PROJECT_1",
                "Campaigns": ["CAMPAIGN_1", "CAMPAIGN_1"],
            },
        ],
        "ProviderDates": [
            {"Date": "2025-01-01T00:00:00Z", "Type": "Insert"},
            {"Date": "2025-01-01T00:00:00Z", "Type": "Update"},
        ],
        "RelatedUrls": [
            {
                "URL": "https://example-distribution.123/TEST/PATH/test_prefix/test_file.txt",
                "Type": "GET DATA",
                "Description": "Download test_file.txt",
            },
            {
                "URL": "s3://test_bucket/test_prefix/test_file.txt",
                "Type": "GET DATA VIA DIRECT ACCESS",
                "Description": (
                    # ruff hint
                    "This link provides direct download access via S3 to test_file.txt"
                ),
            },
        ],
        "SpatialExtent": {
            "HorizontalSpatialDomain": {
                "Geometry": {
                    "GPolygons": [
                        {
                            "Boundary": {
                                "Points": [
                                    {
                                        "Latitude": 1.0,
                                        "Longitude": 2.0,
                                    },
                                    {
                                        "Latitude": 3.0,
                                        "Longitude": 4.0,
                                    },
                                    {
                                        "Latitude": 5.0,
                                        "Longitude": 6.0,
                                    },
                                    {
                                        "Latitude": 7.0,
                                        "Longitude": 8.0,
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        },
        "TemporalExtent": {
            "RangeDateTime": {
                "BeginningDateTime": "2024-01-01T00:00:00Z",
                "EndingDateTime": "2024-01-02T00:00:00Z",
            },
        },
        "TilingIdentificationSystem": {
            "TilingIdentificationSystemName": "TILING_IDENTIFICATION_SYSTEM_1",
            "Coordinate1": {},
            "Coordinate2": {},
        },
    }


def test_get_ummg_date_format_override(granule):
    class CustomUmmg(LocalUmmgBase):
        def get_umm_date_time_format(self) -> str:
            return "%Y-%m-%dT%H:%M:%S.%fZ"

    ummg_obj = CustomUmmg(granule)
    ummg_obj.now = datetime.datetime(2025, 1, 1)

    ummg_dict = ummg_obj.get_ummg()

    assert ummg_dict == {
        "CollectionReference": {
            "ShortName": "TEST_CMR_SHORT_NAME",
            "Version": "1",
        },
        "GranuleUR": "TEST_GRANULE_ID",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5",
            "Version": "1.6.5",
        },
        "ProviderDates": [
            {"Date": "2025-01-01T00:00:00.000000Z", "Type": "Insert"},
            {"Date": "2025-01-01T00:00:00.000000Z", "Type": "Update"},
        ],
    }

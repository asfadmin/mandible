from datetime import datetime
from typing import List, Tuple

import pytest

from mandible.umm_generator.base import Umm
from mandible.umm_generator.umm_g import (
    AdditionalAttribute,
    CollectionReferenceShortNameVersion,
    DataGranule,
    Identifier,
    PGEVersionClass,
    UmmG,
)


def test_custom_umm():
    class TestComponent(Umm):
        Field1: str
        Field2: int

        def get_Field1(self, metadata) -> str:
            return metadata["field_1"]

        def get_Field2(self, metadata) -> int:
            return metadata["field_2"]

    class TestMain(Umm):
        Name: str
        Component: TestComponent

        def get_Name(self, metadata) -> str:
            return metadata["name"]

    metadata = {
        "field_1": "Value 1",
        "field_2": "Value 2",
        "name": "Test Name",
    }
    item = TestMain(metadata)

    assert item.Name == "Test Name"
    assert item.to_dict() == {
        "Name": "Test Name",
        "Component": {
            "Field1": "Value 1",
            "Field2": "Value 2",
        }
    }


def test_custom_error_missing_handler():
    class TestUmm(Umm):
        Field1: str

    with pytest.raises(
        RuntimeError,
        match=(
            "Missing value for 'TestUmm.Field1'. Try implementing a "
            "'get_Field1' method"
        ),
    ):
        TestUmm({})


def test_custom_error_default_and_handler():
    class TestUmm(Umm):
        Field1: str = "default"

        def get_Field1(self, metadata) -> str:
            return metadata["field_1"]

    with pytest.raises(
        RuntimeError,
        match=(
            "Found both explicit value and handler function for "
            "'TestUmm.Field1'"
        ),
    ):
        TestUmm({})


def test_custom_error_tuple_non_ummg():
    class TestUmm(Umm):
        Field1: Tuple[str]

    with pytest.raises(
        RuntimeError,
        match="Non-Umm element of tuple type found for 'TestUmm.Field1'",
    ):
        TestUmm({})


def test_umm_g_abstract():
    with pytest.raises(Exception):
        _ = UmmG({})


def test_umm_g():
    class CustomOrbitNumberAdditionalAttribute(AdditionalAttribute):
        Name: str = "OrbitNumber"

        def get_Values(self, metadata: dict) -> List[str]:
            return [str(metadata["ProductMd"]["orbit_number"])]

    class CustomCollectionReference(CollectionReferenceShortNameVersion):
        ShortName: str = "FOOBAR"
        Version: str = "10"

    class CustomIdentifier(Identifier):
        Identifier: str
        IdentifierType: str = "ProducerGranuleId"

        def get_Identifier(self, metadata: dict) -> str:
            return metadata["granule"]["granuleId"]

    class CustomDataGranule(DataGranule):
        ArchiveAndDistributionInformation: list = []
        Identifiers: Tuple[CustomIdentifier]

        def get_ProductionDateTime(self, metadata: dict) -> datetime:
            return datetime.strptime(
                metadata["ProductMd"]["start_date"],
                "%Y-%m-%d",
            )

    class CustomPGEVersionClass(PGEVersionClass):
        PGEName: str
        PGEVersion: str

        def get_PGEName(self, metadata: dict) -> str:
            return metadata["ProductMd"]["pge_version_string"].split()[0]

        def get_PGEVersion(self, metadata: dict) -> str:
            return metadata["ProductMd"]["pge_version_string"].split()[1]

    class BasicUmmG(UmmG):
        AdditionalAttributes: Tuple[
            CustomOrbitNumberAdditionalAttribute,
        ]
        CollectionReference: CustomCollectionReference
        DataGranule: CustomDataGranule
        PGEVersionClass: CustomPGEVersionClass

    metadata = {
        "granule": {
            "granuleId": "SomeGranuleId",
        },
        "ProductMd": {
            "orbit_number": 1234,
            "start_date": "2024-10-16",
            "pge_version_string": "SomePGE 1.000.2"
        },
    }
    umm_g = BasicUmmG(metadata)

    assert len(umm_g.AdditionalAttributes) == 1
    assert umm_g.AdditionalAttributes[0].Name == "OrbitNumber"
    assert umm_g.AdditionalAttributes[0].Values == ["1234"]
    assert umm_g.CollectionReference.ShortName == "FOOBAR"
    assert umm_g.CollectionReference.Version == "10"

    assert umm_g.to_dict() == {
        "AdditionalAttributes": [
            {
                "Name": "OrbitNumber",
                "Values": ["1234"],
            },
        ],
        "CollectionReference": {
            "ShortName": "FOOBAR",
            "Version": "10",
        },
        "DataGranule": {
            "ArchiveAndDistributionInformation": [],
            "DayNightFlag": "Unspecified",
            "Identifiers": [
                {
                    "Identifier": "SomeGranuleId",
                    "IdentifierType": "ProducerGranuleId",
                },
            ],
            "ProductionDateTime": datetime(2024, 10, 16),
        },
        "GranuleUR": "SomeGranuleId",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5",
            "Version": "1.6.5",
        },
        "PGEVersionClass": {
            "PGEName": "SomePGE",
            "PGEVersion": "1.000.2",
        },
    }

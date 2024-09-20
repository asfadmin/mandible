import pytest

from mandible.umm_generator.base import Umm
from mandible.umm_generator.umm_g import CollectionReference, UmmG


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


def test_umm_g_abstract():
    with pytest.raises(Exception):
        _ = UmmG({})


def test_umm_g():
    class CustomCollectionReference(CollectionReference):
        ShortName: str = "FOOBAR"
        Version: str = "10"

    class BasicUmmG(UmmG):
        AdditionalAttributes = []
        CollectionReference: CustomCollectionReference

    metadata = {
        "granule": {
            "granuleId": "SomeGranuleId",
        },
    }
    umm_g = BasicUmmG(metadata)

    assert umm_g.AdditionalAttributes == []
    assert umm_g.CollectionReference.ShortName == "FOOBAR"
    assert umm_g.CollectionReference.Version == "10"

    assert umm_g.to_dict() == {
        "AdditionalAttributes": [],
        "CollectionReference": {
            "ShortName": "FOOBAR",
            "Version": "10",
        },
        "GranuleUR": "SomeGranuleId",
        "MetadataSpecification": {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5",
            "Version": "1.6.5",
        },
    }

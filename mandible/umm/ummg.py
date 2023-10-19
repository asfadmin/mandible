from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from mandible.umm.ummg_types import (
    AdditionalAttribute,
    ArchiveDistributionInformation,
    CollectionReference,
    DataGranule,
    DataIdentifiers,
    FileMd,
    Metadata,
    MetadataSpecification,
    PgeVersion,
    Platform,
    ProviderDate,
    RelatedUrl,
    SpatialExtent,
    TemporalExtent,
    Ummg,
)

# ISO 8601 with Z
UMM_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _remove_missing(ummg: Ummg) -> Ummg:
    return {k: v for k, v in ummg.items() if v}


class UmmgBase:
    def __init__(self, metadata: Metadata):
        self.now = datetime.now(timezone.utc)
        self.set_product_metadata(metadata)
        self.set_product_files(metadata)
        self.set_collection_info_table(metadata)

    # object setters
    def set_collection_info_table(self, metadata: Metadata):
        self.collection_info_table = metadata["collection_info"]

    def set_product_metadata(self, metadata: Metadata):
        self.product_metadata = metadata["product_md"]

    def set_product_files(self, metadata: Metadata):
        self.product_files = metadata["product_files_md"]

    # general getters used in the ummg getters
    def get_file_name_path(self) -> Path:
        return Path(self.get_product_file_metadata()["name"])

    def get_file_type(self) -> str:
        file_type = {
            ".bin": "Binary",
            ".gpkg": "GeoPackage",
            ".h5": "HDF5",
            ".json": "JSON",
            ".xml": "XML",
        }
        file_ext = self.get_file_name_path().suffix
        return file_type.get(file_ext, "ASCII")

    def get_product_file_metadata(self) -> FileMd:
        return self.product_files["product_file"]

    def get_mission(self) -> str:
        return self.product_metadata["mission"]

    def get_provider_time(self) -> datetime:
        return self.now

    def get_product_creation_time(self) -> datetime:
        return self.product_metadata["product_creation_datetime"]

    def get_product_start_time(self) -> datetime:
        return self.product_metadata["product_start_time"]

    def get_product_end_time(self) -> datetime:
        return self.product_metadata["product_stop_time"]

    def get_archive_distribution_information(self) -> List[ArchiveDistributionInformation]:
        return [{
            "Name": self.get_file_name(),
            "SizeInBytes": self.get_product_file_size(),
            "Format": self.get_file_type(),
        }]

    def get_data_identifiers(self) -> List[DataIdentifiers]:
        return [{
            "Identifier": self.get_scene_id(),
            "IdentifierType": "ProducerGranuleId"
        }]

    def get_collection_long_name(self) -> str:
        return self.collection_info_table["long_name"]

    def get_collection_short_name(self) -> str:
        return self.collection_info_table["short_name"]

    def get_scene_id(self) -> str:
        return self.get_file_name_path().name.split(".", 1)[0]

    def get_file_name(self) -> str:
        return str(self.get_file_name_path())

    def get_product_url(self) -> str:
        return self.get_product_file_metadata()["uri"]

    def get_product_s3_uri(self) -> str:
        return self.get_product_file_metadata()["s3uri"]

    def get_product_file_size(self) -> int:
        return self.get_product_file_metadata()["size"]

    # Start of getters that handle the big picture
    def get_additional_attributes(self) -> Optional[List[AdditionalAttribute]]:
        return None

    def get_collection_reference(self) -> CollectionReference:
        return {
            "EntryTitle": self.get_collection_long_name()
        }

    def get_data_granule(self) -> DataGranule:
        return {
            "ArchiveAndDistributionInformation": self.get_archive_distribution_information(),
            "DayNightFlag": "Unspecified",
            "Identifiers": self.get_data_identifiers(),
            "ProductionDateTime": self.get_product_creation_time().strftime(UMM_DATETIME_FORMAT),
        }

    def get_granule_ur(self) -> str:
        return self.get_file_name_path().name.replace(".", "-")

    def get_metadata_specification(self) -> MetadataSpecification:
        return {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.4",
            "Version": "1.6.4"
        }

    def get_pge_version(self) -> Optional[PgeVersion]:
        return None

    def get_platforms(self) -> List[Platform]:
        return [{
            "ShortName": self.get_mission()
        }]

    def get_provider_dates(self) -> List[ProviderDate]:
        return [
            {"Type": "Insert", "Date": self.get_provider_time().strftime(UMM_DATETIME_FORMAT)},
            {"Type": "Update", "Date": self.get_provider_time().strftime(UMM_DATETIME_FORMAT)},
        ]

    def get_related_urls(self) -> Optional[List[RelatedUrl]]:
        return [
            {
                "URL": self.get_product_url(),
                "Type": "GET DATA",
                "Subtype": "VERTEX"
            },
            {
                "URL": self.get_product_s3_uri(),
                "Type": "GET DATA VIA DIRECT ACCESS"
            }
        ]

    def get_spatial_extent(self) -> Optional[SpatialExtent]:
        return None

    def get_temporal_extent(self) -> Optional[TemporalExtent]:
        return {
            "RangeDateTime": {
                "BeginningDateTime": self.get_product_start_time().strftime(UMM_DATETIME_FORMAT),
                "EndingDateTime": self.get_product_end_time().strftime(UMM_DATETIME_FORMAT),
            }
        }

    def get_input_granules(self) -> Optional[List[str]]:
        return None

    def get_ummg(self) -> Ummg:
        parsed_ummg: Ummg = {
            "AdditionalAttributes": self.get_additional_attributes(),
            "CollectionReference": self.get_collection_reference(),
            "DataGranule": self.get_data_granule(),
            "GranuleUR": self.get_granule_ur(),
            "MetadataSpecification": self.get_metadata_specification(),
            "PGEVersionClass": self.get_pge_version(),
            "Platforms": self.get_platforms(),
            "ProviderDates": self.get_provider_dates(),
            "RelatedUrls": self.get_related_urls(),
            "SpatialExtent": self.get_spatial_extent(),
            "TemporalExtent": self.get_temporal_extent(),
            "InputGranules": self.get_input_granules()
        }
        return _remove_missing(parsed_ummg)

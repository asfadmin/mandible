from datetime import datetime, timezone
from pathlib import Path
from typing import List

# ISO 8601 with Z
UMM_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def _remove_missing(ummg: dict) -> dict:
    return {k: v for k, v in ummg.items() if v}


class UmmgBase():
    """
    Relies on keys that are required to extract metadata

    CollectionRef:
        ShortName: str
        LongName: str
    ProductMd:
        productCreationDateTime: datetime
        productStartTime: datetime
        productStopTime: datetime
    FileMd:
        productFile: {
            name: str,
            uri: str,
            s3uri: str,
            size: str,
            key: str,
            bucket: str,
        }
        relatedFiles: [
            {
                name: str,
                uri: str,
                s3uri: str,
                size: str,
                key: str,
                bucket: str,
            }
        ]

    """
    def __init__(self, meta: dict):
        self.now = datetime.now(timezone.utc)
        self.set_product_metadata(meta)
        self.set_product_files(meta)
        self.set_product_file_md()
        self.set_collection_ref_table(meta)
        self.set_file_name()
        self.file_type = {
            ".bin": "Binary",
            ".gpkg": "GeoPackage",
            ".h5": "HDF5",
            ".json": "JSON",
            ".xml": "XML",
        }

    # object setters
    def set_collection_ref_table(self, meta: dict):
        self.collection_ref_table = meta["CollectionRef"]

    def set_product_metadata(self, meta: dict):
        self.product_metadata = meta["ProductMd"]

    def set_product_files(self, meta: dict):
        self.product_files = meta["FileMd"]

    def set_file_name(self):
        self.file_name = Path(self.product_file_md["name"])

    def set_product_file_md(self):
        self.product_file_md = self.product_files["productFile"]

    # general getters used in the ummg getters
    def get_file_type(self) -> str:
        file_ext = self.file_name.suffix
        return self.file_type.get(file_ext, "ASCII")

    def get_mission(self) -> str:
        return self.product_metadata["mission"]

    def get_provider_time(self) -> datetime:
        return self.now

    def get_product_creation_time(self) -> datetime:
        return self.product_metadata["productCreationDateTime"]

    def get_product_start_time(self) -> datetime:
        return self.product_metadata["productStartTime"]

    def get_product_end_time(self) -> datetime:
        return self.product_metadata["productStopTime"]

    def get_archive_distribution_information(self) -> List[dict]:
        return [{
            "Name": self.get_file_name(),
            "SizeInBytes": self.get_product_file_size(),
            "Format": self.get_file_type(),
        }]

    def get_data_identifiers(self) -> List[dict]:
        return [{
            "Identifier": self.get_scene_id(),
            "IdentifierType": "ProducerGranuleId"
        }]

    def get_collection_long_name(self) -> str:
        return self.collection_ref_table["LongName"]

    def get_collection_short_name(self) -> str:
        return self.collection_ref_table["ShortName"]

    def get_scene_id(self) -> str:
        return self.file_name.name.split(".", 1)[0]

    def get_file_name(self) -> str:
        return str(self.file_name)

    def get_product_url(self) -> str:
        return self.product_file_md["uri"]

    def get_product_s3_uri(self) -> str:
        return self.product_file_md["s3uri"]

    def get_product_file_size(self) -> str:
        return self.product_file_md["size"]

    def get_product_key(self) -> str:
        return self.product_file_md["key"]

    def get_product_bucket(self) -> str:
        return self.product_file_md["bucket"]

    # Start of getters that handle the big picture
    def get_additional_attributes(self) -> List[dict]:
        return []

    def get_collection_reference(self) -> dict:
        return {
            "EntryTitle": self.get_collection_long_name()
        }

    def get_data_granule(self) -> dict:
        return {
            "ArchiveAndDistributionInformation": self.get_archive_distribution_information(),
            "DayNightFlag": "Unspecified",
            "Identifiers": self.get_data_identifiers(),
            "ProductionDateTime": self.get_product_creation_time().strftime(UMM_DATETIME_FORMAT),
        }

    def get_granule_ur(self) -> str:
        return self.file_name.name.replace(".", "-")

    def get_metadata_specification(self) -> dict:
        return {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.4",
            "Version": "1.6.4"
        }

    def get_pge_version(self) -> dict:
        return {}

    def get_platforms(self) -> List[dict]:
        return [{
            "ShortName": self.get_mission()
        }]

    def get_provider_dates(self) -> List[dict]:
        return [
            {"Type": "Insert", "Date": self.get_provider_time().strftime(UMM_DATETIME_FORMAT)},
            {"Type": "Update", "Date": self.get_provider_time().strftime(UMM_DATETIME_FORMAT)},
        ]

    def get_related_urls(self) -> List[dict]:
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

    def get_spatial_extent(self) -> dict:
        return {}

    def get_temporal_extent(self) -> dict:
        return {
            "RangeDateTime": {
                "BeginningDateTime": self.get_product_start_time().strftime(UMM_DATETIME_FORMAT),
                "EndingDateTime": self.get_product_end_time().strftime(UMM_DATETIME_FORMAT),
            }
        }

    def get_input_granules(self) -> List[str]:
        return []

    def get_ummg(self) -> dict:
        ummg = {
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
        return _remove_missing(ummg)

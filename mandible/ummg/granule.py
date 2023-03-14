
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from shapely import wkt
from ummg.error import UmmgFileNotFound

UMM_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
PRODUCT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
FILE_TYPE = {
    ".bin": "Binary",
    ".gpkg": "GeoPackage",
    ".h5": "HDF5",
    ".json": "JSON",
    ".xml": "XML",
}


def create_poly_points_from_wkt(wkt_str: str) -> list:
    poly = wkt.loads(wkt_str)
    x, y = poly.exterior.coords.xy
    points = list(zip(y, x))
    if len(points) > 1 and points[-1] == points[-2]:
        return points[:-1]
    return points


def to_umm_datetime(value: str, format: str = PRODUCT_DATETIME_FORMAT):
    return datetime.strptime(
        round_nano_seconds_to_micro(value),
        format
    ).strftime(UMM_DATETIME_FORMAT)


def round_nano_seconds_to_micro(time_str: str) -> str:
    root, fractional_seconds = time_str.rsplit(".", 1)
    fractional_seconds = fractional_seconds.replace("Z", "")
    fractional_seconds = str(round(float(f".{fractional_seconds}"), 6))
    return f"{root}.{fractional_seconds[2:]}"


def _remove_missing(ummg: dict) -> dict:
    return {k: v for k, v in ummg.items() if v}


def _get_file_by_ext(product_files: dict, ext: str) -> dict:
    ext_pattern = re.compile(ext)
    filtered_product_files = [file for file in product_files if ext_pattern.fullmatch(Path(file["name"]).suffix)]
    if len(filtered_product_files) > 1:
        raise Exception("More than one product file found in product files")
    if not filtered_product_files:
        return {}
    return filtered_product_files[0]


class UmmgBase():
    """
    Relies on keys that are required to extract metadata
    CollectionRef:
        ShortName: str
        LongName: str
    ProductMd:
        productCreationDateTime: datetime str
        productStartTime: datetime str
        productStopTime: datetime str
    FileMd:
        movedFiles: List[Dict]
            uri: str
            s3uri: str
            size: str
            key: str
            bucket: str
    """
    def __init__(self, meta: dict):
        self.now = datetime.now(timezone.utc).strftime(PRODUCT_DATETIME_FORMAT)
        self.set_product_metadata(meta)
        self.set_product_files(meta)
        self.set_product_file_md()
        self.set_collection_ref_table(meta)
        self.set_file_name()

    def set_collection_ref_table(self, meta: dict):
        self.collection_ref_table = meta["CollectionRef"]

    def set_product_metadata(self, meta: dict):
        self.product_metadata = meta["ProductMd"]

    def set_product_files(self, meta: dict):
        self.product_files = meta["FileMd"]["movedFiles"]

    def set_file_name(self):
        self.file_name = Path(self.product_file_md["name"])

    def set_product_file_md(self):
        self.product_file_md = _get_file_by_ext(self.product_files, r"\.xml")
        if not self.product_file_md:
            raise UmmgFileNotFound("XML")

    def get_file_type(self) -> str:
        file_ext = self.file_name.suffix
        return FILE_TYPE.get(file_ext, "ASCII")

    def get_mission(self) -> str:
        return ""

    def get_provider_time(self) -> str:
        return to_umm_datetime(self.now)

    def get_product_creation_time(self) -> str:
        return to_umm_datetime(self.product_metadata["productCreationDateTime"])

    def get_product_start_time(self) -> str:
        return to_umm_datetime(self.product_metadata["productStartTime"])

    def get_product_end_time(self) -> str:
        return to_umm_datetime(self.product_metadata["productStopTime"])

    def get_temporal_extent(self) -> dict:
        return {
            "RangeDateTime": {
                "BeginningDateTime": self.get_product_start_time(),
                "EndingDateTime": self.get_product_end_time(),
            }
        }

    def get_provider_dates(self) -> List[dict]:
        return [
            {"Type": "Insert", "Date": self.get_provider_time()},
            {"Type": "Update", "Date": self.get_provider_time()},
        ]

    def get_collection_long_name(self) -> str:
        return self.collection_ref_table["LongName"]

    def get_collection_short_name(self) -> str:
        return self.collection_ref_table["ShortName"]

    def get_scene_id(self) -> str:
        return self.file_name.name.split(".", 1)[0]

    def get_granule_ur(self) -> str:
        return self.file_name.name.replace(".", "-")

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

    def get_pge_version(self) -> dict:
        return {}

    def get_spatial_extent(self) -> dict:
        return {}

    def get_input_granules(self) -> List[str]:
        return []

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

    def get_metadata_specification(self) -> dict:
        return {
            "Name": "UMM-G",
            "URL": "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.4",
            "Version": "1.6.4"
        }

    def get_additional_attributes(self) -> List[dict]:
        return []

    def get_ummg(self) -> dict:
        ummg = {
            "AdditionalAttributes": self.get_additional_attributes(),
            "CollectionReference": {
                "EntryTitle": self.get_collection_long_name()
            },
            "DataGranule": {
                "ArchiveAndDistributionInformation": [
                    {
                        "Name": self.get_file_name(),
                        "SizeInBytes": self.get_product_file_size(),
                        "Format": self.get_file_type(),
                    }
                ],
                "DayNightFlag": "Unspecified",
                "Identifiers": [
                    {
                        "Identifier": self.get_scene_id(),
                        "IdentifierType": "ProducerGranuleId"
                    }
                ],
                "ProductionDateTime": self.get_product_creation_time(),
            },
            "GranuleUR": self.get_granule_ur(),
            "MetadataSpecification": self.get_metadata_specification(),
            "PGEVersionClass": self.get_pge_version(),
            "Platforms": [
                {
                    "ShortName": self.get_mission()
                }
            ],
            "ProviderDates": self.get_provider_dates(),
            "RelatedUrls": self.get_related_urls(),
            "SpatialExtent": self.get_spatial_extent(),
            "TemporalExtent": self.get_temporal_extent(),
            "InputGranules": self.get_input_granules()
        }
        return _remove_missing(ummg)

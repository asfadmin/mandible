from __future__ import annotations

from datetime import datetime
from typing import List

from typing_extensions import NotRequired, TypedDict


class FileMd(TypedDict, total=False):
    name: str
    uri: str
    s3uri: str
    size: int


class CollectionInfo(TypedDict, total=False):
    short_name: str
    long_name: str


class ProductMd(TypedDict, total=False):
    product_creation_datetime: datetime
    product_start_time: datetime
    product_stop_time: datetime
    mission: str


class ProductFilesMd(TypedDict, total=False):
    product_file: FileMd
    related_Files: List[FileMd]


class Metadata(TypedDict, total=False):
    collection_info: CollectionInfo
    product_md: ProductMd
    product_files_md: ProductFilesMd


class ArchiveDistributionInformation(TypedDict, total=False):
    Name: str
    SizeInBytes: int
    Format: str


class DataIdentifiers(TypedDict, total=False):
    Identifier: str
    IdentifierType: str


class CollectionReference(TypedDict, total=False):
    EntryTitle: str


class DataGranules(TypedDict, total=False):
    ArchiveAndDistributionInformation: ArchiveDistributionInformation
    DayNightFlag: str
    Identifiers: DataIdentifiers
    ProductionDateTime: str


class MetadataSpecification(TypedDict, total=False):
    Name: str
    URL: str
    Version: str


class ProviderDates(TypedDict, total=False):
    Type: str
    Date: str


class RelatedUrl(TypedDict, total=False):
    URL: str
    Type: str
    SubType: NotRequired[str]


class PgeVersion(TypedDict, total=False):
    PGEVersion: str


class Platform(TypedDict, total=False):
    ShortName: str


class RangeDateTime(TypedDict, total=False):
    BeginningDateTime: str
    EndingDateTime: str


class TemporalExtent(TypedDict, total=False):
    RangeDateTime: RangeDateTime


class SpatialExtent(TypedDict, total=False):
    HorizontalSpatialDomain: NotRequired[dict]

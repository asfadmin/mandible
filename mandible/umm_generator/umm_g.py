from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union

from .base import Umm

UMM_DATE_FORMAT = "%Y-%m-%d"
UMM_DATETIME_FORMAT = f"{UMM_DATE_FORMAT}T%H:%M:%SZ"


# AdditionalAttributes
class AdditionalAttribute(Umm):
    Name: str
    Values: Sequence[str]


# CollectionReference
class CollectionReferenceShortNameVersion(Umm):
    ShortName: str
    Version: str


class CollectionReferenceEntryTitle(Umm):
    EntryTitle: str


CollectionReference = Union[
    CollectionReferenceShortNameVersion,
    CollectionReferenceEntryTitle,
]


# DataGranule
# ArchiveAndDistributionInformation
class Checksum(Umm):
    Value: str
    Algorithm: str


class ArchiveAndDistributionInformation(Umm):
    Name: str
    SizeInBytes: Optional[int] = None
    Size: Optional[int] = None
    SizeUnit: Optional[str] = None
    Format: Optional[str] = None
    FormatType: Optional[str] = None
    MimeType: Optional[str]
    Checksum: Optional[Checksum] = None


class Identifier(Umm):
    IdentifierType: str
    Identifier: str
    IdentifierName: Optional[str] = None


class DataGranule(Umm):
    ArchiveAndDistributionInformation: Optional[
        Sequence[ArchiveAndDistributionInformation]
    ] = None
    DayNightFlag: str = "Unspecified"
    Identifiers: Optional[Sequence[Identifier]] = None
    ProductionDateTime: datetime
    ReprocessingActual: Optional[str] = None
    ReprocessingPlanned: Optional[str] = None


# MetadataSpecification
class MetadataSpecification(Umm):
    Name: str = "UMM-G"
    URL: str = "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5"
    Version: str = "1.6.5"


# PGEVersionClass
class PGEVersionClass(Umm):
    PGEName: Optional[str] = None
    PGEVersion: str


class UmmG(Umm):
    # Sorted?
    AdditionalAttributes: Optional[Sequence[AdditionalAttribute]] = None
    CollectionReference: CollectionReference
    DataGranule: Optional[DataGranule] = None
    GranuleUR: str
    MetadataSpecification: MetadataSpecification
    # OrbitCalculatedSpatialDomains: Optional[self.get_orbit_calculated_spatial_domains()]
    PGEVersionClass: Optional[PGEVersionClass] = None
    # Platforms: Optional[self.get_platforms()]
    # Projects: Optional[self.get_projects()]
    # ProviderDates: self.get_provider_dates(),
    # RelatedUrls: Optional[self.get_related_urls()]
    # SpatialExtent: Optional[self.get_spatial_extent()]
    # TemporalExtent: Optional[self.get_temporal_extent()]
    # InputGranules: Optional[self.get_input_granules()]

    def get_GranuleUR(self, metadata: Dict[str, Any]) -> str:
        return metadata["granule"]["granuleId"]

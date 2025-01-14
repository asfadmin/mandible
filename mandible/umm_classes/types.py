"""UMM-G and Cumulus type definitions used by UmmgBase"""

from typing import Any, Union

from typing_extensions import NotRequired, TypedDict

# JSONSchema definitions are available here:
# https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule


class AccessConstraints(TypedDict):
    """AccessConstraints type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#195
    """
    Description: NotRequired[str]
    Value: Union[float, int]


class AdditionalAttribute(TypedDict):
    """AdditionalAttribute type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1057
    """
    Name: str
    Values: list[str]


class ArchiveAndDistributionInformationFilePackageType(TypedDict):
    """ArchiveAndDistributionInformation type definition for FilePackageType.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#263
    """
    Name: str
    SizeInBytes: NotRequired[int]
    Size: NotRequired[Union[float, int]]
    SizeUnit: NotRequired[str]
    Format: NotRequired[str]
    MimeType: NotRequired[str]
    Checksum: NotRequired["Checksum"]
    Files: NotRequired[list["ArchiveAndDistributionInformationFileType"]]


class ArchiveAndDistributionInformationFileType(TypedDict):
    """ArchiveAndDistributionInformation type definition for FileType.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#309
    """
    Name: str
    SizeInBytes: NotRequired[int]
    Size: NotRequired[Union[float, int]]
    SizeUnit: NotRequired[str]
    Format: NotRequired[str]
    FormatType: NotRequired[str]
    MimeType: NotRequired[str]
    Checksum: NotRequired["Checksum"]


ArchiveAndDistributionInformation = Union[
    ArchiveAndDistributionInformationFileType,
    ArchiveAndDistributionInformationFilePackageType,
]


class BoundingRectangle(TypedDict):
    """BoundingRectangle type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#591
    """
    WestBoundingCoordinate: Union[float, int]
    NorthBoundingCoordinate: Union[float, int]
    EastBoundingCoordinate: Union[float, int]
    SouthBoundingCoordinate: Union[float, int]


class Boundary(TypedDict):
    """Boundary type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#625
    """
    Points: list["Point"]


class Characteristic(TypedDict):
    """Characteristic type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1008
    """
    Name: str
    Value: str


class Checksum(TypedDict):
    """CollectionReference type definition with ShortName and Version.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1159
    """
    Value: str
    Algorithm: str


class CollectionReferenceShortNameVersion(TypedDict):
    """CollectionReference type definition with ShortName and Version.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#166
    """
    ShortName: str
    Version: str


class CollectionReferenceEntryTitle(TypedDict):
    """CollectionReference type definition with EntryTitle.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#184
    """
    EntryTitle: str


CollectionReference = Union[
    CollectionReferenceEntryTitle,
    CollectionReferenceShortNameVersion,
]


class DataGranule(TypedDict):
    """DataGranule type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#213
    """
    ArchiveAndDistributionInformation: NotRequired[list[ArchiveAndDistributionInformation]]
    ReprocessingPlanned: NotRequired[str]
    ReprocessingActual: NotRequired[str]
    DayNightFlag: str
    ProductionDateTime: str
    Identifiers: NotRequired[list["Identifier"]]


class ExclusiveZone(TypedDict):
    """ExclusiveZone type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#640
    """
    Boundaries: list[Boundary]


class Geometry(TypedDict):
    """Geometry type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#525
    """
    Points: NotRequired[list["Point"]]
    BoundingRectangles: NotRequired[list[BoundingRectangle]]
    GPolygons: NotRequired[list["GPolygon"]]
    Lines: NotRequired[list["Line"]]


class GPolygon(TypedDict):
    """GPolygon type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#611
    """
    Boundary: Boundary
    ExclusiveZone: NotRequired[ExclusiveZone]


class HorizontalSpatialDomain(TypedDict):
    """HorizontalSpatialDomain type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#497
    """
    # TODO(reweeden): Implement
    ZoneIdentifier: NotRequired[dict[str, Any]]
    Geometry: NotRequired[Geometry]
    # TODO(reweeden): Implement
    Orbit: NotRequired[dict[str, Any]]
    # TODO(reweeden): Implement
    Track: NotRequired[dict[str, Any]]


class Identifier(TypedDict):
    """Identifier type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#353
    """
    Identifier: str
    IdentifierType: str
    IdentifierName: NotRequired[str]


class Instrument(TypedDict):
    """Instrument type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#968
    """
    ShortName: str
    Characteristics: NotRequired[list[Characteristic]]
    ComposedOf: NotRequired[list["Instrument"]]
    OperationalModes: NotRequired[list[str]]


class Line(TypedDict):
    """Line type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#655
    """
    Points: list["Point"]


class MeasuredParameter(TypedDict):
    """MeasuredParameter type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#840
    """
    ParameterName: str
    # TODO(reweeden): Implement
    QAStats: NotRequired[dict[str, Any]]
    # TODO(reweeden): Implement
    QAFlags: NotRequired[dict[str, Any]]


class MetadataSpecification(TypedDict):
    """MetadataSpecification type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1285
    """
    URL: str
    Name: str
    Version: str


class OrbitCalculatedSpatialDomain(TypedDict):
    """OrbitCalculatedSpatialDomain type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#786
    """
    OrbitalModelName: NotRequired[str]
    OrbitNumber: NotRequired[int]
    BeginOrbitNumber: NotRequired[int]
    EndOrbitNumber: NotRequired[int]
    EquatorCrossingLongitude: NotRequired[Union[float, int]]
    EquatorCrossingDateTime: NotRequired[str]


class PGEVersionClass(TypedDict):
    """PGEVersionClass type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#403
    """
    PGEName: NotRequired[str]
    PGEVersion: str


class Platform(TypedDict):
    """Platform type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#949
    """
    ShortName: str
    Instruments: NotRequired[list[Instrument]]


class Point(TypedDict):
    """GPolygon type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#611
    """
    Longitude: Union[float, int]
    Latitude: Union[float, int]


class Project(TypedDict):
    """Project type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1028
    """
    ShortName: str
    Campaigns: NotRequired[list[str]]


class ProviderDate(TypedDict):
    """ProviderDate type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#144
    """
    Date: str
    Type: str


class RangeDateTime(TypedDict):
    """RangeDateTime type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#447
    """
    BeginningDateTime: str
    EndingDateTime: NotRequired[str]


class RelatedUrl(TypedDict):
    """RelatedUrl type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1112
    """
    URL: str
    Type: str
    Subtype: NotRequired[str]
    Description: NotRequired[str]
    Format: NotRequired[str]
    MimeType: NotRequired[str]
    Size: NotRequired[Union[float, int]]
    SizeUnit: NotRequired[str]


class SpatialExtent(TypedDict):
    """SpatialExtent type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#465
    """
    # TODO(reweeden): Implement
    GranuleLocalities: NotRequired[list[dict[str, Any]]]
    HorizontalSpatialDomain: NotRequired["HorizontalSpatialDomain"]
    # TODO(reweeden): Implement
    VerticalSpatialDomains: NotRequired[list[dict[str, Any]]]


class TemporalExtentRangeDateTime(TypedDict):
    """TemporalExtent type definition with RangeDateTime.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#428
    """
    RangeDateTime: RangeDateTime


class TemporalExtentSingleDateTime(TypedDict):
    """TemporalExtent type definition with SingleDateTime.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#437
    """
    SingleDateTime: str


TemporalExtent = Union[
    TemporalExtentRangeDateTime,
    TemporalExtentSingleDateTime,
]


class TilingIdentificationSystem(TypedDict):
    """TilingIdentificationSystem type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#1081
    """
    TilingIdentificationSystemName: str
    # TODO(reweeden): Implement
    Coordinate1: dict[str, Any]
    # TODO(reweeden): Implement
    Coordinate2: dict[str, Any]


class Ummg(TypedDict):
    """UMM-G type definition.

    https://git.earthdata.nasa.gov/projects/EMFD/repos/unified-metadata-model/browse/granule/v1.6.5/umm-g-json-schema.json#7
    """
    GranuleUR: str
    ProviderDates: list[ProviderDate]
    CollectionReference: CollectionReference
    AccessConstraints: NotRequired[AccessConstraints]
    DataGranule: NotRequired[DataGranule]
    PGEVersionClass: NotRequired[PGEVersionClass]
    TemporalExtent: NotRequired[TemporalExtent]
    SpatialExtent: NotRequired[SpatialExtent]
    OrbitCalculatedSpatialDomains: NotRequired[list[OrbitCalculatedSpatialDomain]]
    MeasuredParameters: NotRequired[list[MeasuredParameter]]
    Platforms: NotRequired[list[Platform]]
    Projects: NotRequired[list[Project]]
    AdditionalAttributes: NotRequired[list[AdditionalAttribute]]
    InputGranules: NotRequired[list[str]]
    TilingIdentificationSystem: NotRequired[TilingIdentificationSystem]
    CloudCover: NotRequired[Union[float, int]]
    RelatedUrls: NotRequired[list[RelatedUrl]]
    NativeProjectionNames: NotRequired[list[str]]
    GridMappingNames: NotRequired[list[str]]
    MetadataSpecification: MetadataSpecification

# Other TypedDict definitions


class CMAGranule(TypedDict, total=False):
    granuleId: str
    files: list["CMAGranuleFile"]


class CMAGranuleFile(TypedDict, total=False):
    bucket: str
    checksum: NotRequired[str]
    checksumType: NotRequired[str]
    fileName: str
    key: str
    size: NotRequired[int]
    type: NotRequired[str]

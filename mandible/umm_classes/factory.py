"""Factory functions for creating small pieces of UMM"""

from typing import Optional, Union

from .types import (
    AccessConstraints,
    AdditionalAttribute,
    ArchiveAndDistributionInformation,
    CollectionReference,
    DataGranule,
    Identifier,
    Instrument,
    MeasuredParameter,
    MetadataSpecification,
    OrbitCalculatedSpatialDomain,
    PGEVersionClass,
    Platform,
    Project,
    ProviderDate,
    RelatedUrl,
    SpatialExtent,
    TemporalExtent,
    TilingIdentificationSystem,
    Ummg,
)


def additional_attribute(name: str, *value: str) -> AdditionalAttribute:
    return {
        "Name": name,
        "Values": list(value),
    }


def data_granule(
    day_night_flag: str,
    production_date_time: str,
    archive_and_distribution_information: Optional[list[ArchiveAndDistributionInformation]] = None,
    reprocessing_planned: Optional[str] = None,
    reprocessing_actual: Optional[str] = None,
    identifiers: Optional[list[Identifier]] = None,
) -> DataGranule:
    obj: DataGranule = {
        "DayNightFlag": day_night_flag,
        "ProductionDateTime": production_date_time,
    }
    if archive_and_distribution_information is not None:
        obj["ArchiveAndDistributionInformation"] = archive_and_distribution_information
    if reprocessing_planned is not None:
        obj["ReprocessingPlanned"] = reprocessing_planned
    if reprocessing_actual is not None:
        obj["ReprocessingActual"] = reprocessing_actual
    if identifiers is not None:
        obj["Identifiers"] = identifiers

    return obj


def identifier(
    type: str,
    identifier: str,
    name: Optional[str] = None,
) -> Identifier:
    obj: Identifier = {
        "IdentifierType": type,
        "Identifier": identifier,
    }
    if name is not None:
        obj["IdentifierName"] = name

    return obj


def metadata_specification(version: str) -> MetadataSpecification:
    return {
        "Name": "UMM-G",
        "URL": f"https://cdn.earthdata.nasa.gov/umm/granule/v{version}",
        "Version": version,
    }


def pge_version_class(name: str, version: str) -> PGEVersionClass:
    return {
        "PGEName": name,
        "PGEVersion": version,
    }


def platform(
    short_name: str,
    instruments: Optional[list[Instrument]] = None,
) -> Platform:
    obj: Platform = {
        "ShortName": short_name,
    }
    if instruments is not None:
        obj["Instruments"] = instruments

    return obj


def provider_date(type: str, date: str) -> ProviderDate:
    return {
        "Type": type,
        "Date": date,
    }


def related_url(
    url: str,
    type: str,
    subtype: Optional[str] = None,
    description: Optional[str] = None,
    format: Optional[str] = None,
    mime_type: Optional[str] = None,
    size: Optional[Union[float, int]] = None,
    size_unit: Optional[str] = None,
) -> RelatedUrl:
    obj: RelatedUrl = {
        "URL": url,
        "Type": type,
    }
    if subtype is not None:
        obj["Subtype"] = subtype
    if description is not None:
        obj["Description"] = description
    if format is not None:
        obj["Format"] = format
    if mime_type is not None:
        obj["MimeType"] = mime_type
    if size is not None:
        obj["Size"] = size
    if size_unit is not None:
        obj["SizeUnit"] = size_unit

    return obj


def ummg(
    granule_ur: str,
    provider_dates: list[ProviderDate],
    collection_reference: CollectionReference,
    metadata_specification: MetadataSpecification,
    access_constraints: Optional[AccessConstraints] = None,
    data_granule: Optional[DataGranule] = None,
    pge_version_class: Optional[PGEVersionClass] = None,
    temporal_extent: Optional[TemporalExtent] = None,
    spatial_extent: Optional[SpatialExtent] = None,
    orbit_calculated_spatial_domains: Optional[list[OrbitCalculatedSpatialDomain]] = None,
    measured_parameters: Optional[list[MeasuredParameter]] = None,
    platforms: Optional[list[Platform]] = None,
    projects: Optional[list[Project]] = None,
    additional_attributes: Optional[list[AdditionalAttribute]] = None,
    input_granules: Optional[list[str]] = None,
    tiling_identification_system: Optional[TilingIdentificationSystem] = None,
    cloud_cover: Optional[Union[float, int]] = None,
    related_urls: Optional[list[RelatedUrl]] = None,
    native_projection_names: Optional[list[str]] = None,
    grid_mapping_names: Optional[list[str]] = None,
) -> Ummg:
    obj: Ummg = {
        "CollectionReference": collection_reference,
        "GranuleUR": granule_ur,
        "MetadataSpecification": metadata_specification,
        "ProviderDates": provider_dates,
    }
    if access_constraints is not None:
        obj["AccessConstraints"] = access_constraints
    if data_granule is not None:
        obj["DataGranule"] = data_granule
    if pge_version_class is not None:
        obj["PGEVersionClass"] = pge_version_class
    if temporal_extent is not None:
        obj["TemporalExtent"] = temporal_extent
    if spatial_extent is not None:
        obj["SpatialExtent"] = spatial_extent
    if orbit_calculated_spatial_domains is not None:
        obj["OrbitCalculatedSpatialDomains"] = orbit_calculated_spatial_domains
    if measured_parameters is not None:
        obj["MeasuredParameters"] = measured_parameters
    if platforms is not None:
        obj["Platforms"] = platforms
    if projects is not None:
        obj["Projects"] = projects
    if additional_attributes is not None:
        obj["AdditionalAttributes"] = additional_attributes
    if input_granules is not None:
        obj["InputGranules"] = input_granules
    if tiling_identification_system is not None:
        obj["TilingIdentificationSystem"] = tiling_identification_system
    if cloud_cover is not None:
        obj["CloudCover"] = cloud_cover
    if related_urls is not None:
        obj["RelatedUrls"] = related_urls
    if native_projection_names is not None:
        obj["NativeProjectionNames"] = native_projection_names
    if grid_mapping_names is not None:
        obj["GridMappingNames"] = grid_mapping_names

    return obj

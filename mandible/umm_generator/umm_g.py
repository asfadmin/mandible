from typing import Any, Dict, Sequence

from .base import Umm


class AdditionalAttribute(Umm):
    Name: str
    Values: Sequence[str]


class CollectionReference(Umm):
    ShortName: str
    Version: str


# class DataGranule:
#     "ArchiveAndDistributionInformation": self.get_archive_and_distribution_information(),
#     "DayNightFlag": "Unspecified",
#     "Identifiers": self.get_identifiers(),
#     "ProductionDateTime": to_umm_str(self.get_product_creation_time()),


class MetadataSpecification(Umm):
    Name: str = "UMM-G"
    URL: str = "https://cdn.earthdata.nasa.gov/umm/granule/v1.6.5"
    Version: str = "1.6.5"


class UmmG(Umm):
    # Sorted?
    AdditionalAttributes: Sequence[AdditionalAttribute]
    CollectionReference: CollectionReference
    # DataGranule: DataGranule
    GranuleUR: str
    MetadataSpecification: MetadataSpecification
    # OrbitCalculatedSpatialDomains: self.get_orbit_calculated_spatial_domains(),
    # PGEVersionClass: self.get_pge_version_class(),
    # Platforms: self.get_platforms(),
    # Projects: self.get_projects(),
    # ProviderDates: self.get_provider_dates(),
    # RelatedUrls: self.get_related_urls(),
    # SpatialExtent: self.get_spatial_extent(),
    # TemporalExtent: self.get_temporal_extent(),
    # InputGranules: self.get_input_granules(),

    def get_GranuleUR(self, metadata: Dict[str, Any]) -> str:
        return metadata["granule"]["granuleId"]

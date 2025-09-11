"""Base classes for implementing UMM-G generation"""

import datetime
import logging
from abc import ABC, abstractmethod
from datetime import timezone
from typing import Optional, Union, overload

from .factory import (
    data_granule,
    identifier,
    metadata_specification,
    platform,
    provider_date,
    range_date_time,
    ummg,
)
from .related_url_builder import RelatedUrlBuilder
from .types import (
    AccessConstraints,
    AdditionalAttribute,
    ArchiveAndDistributionInformation,
    CMAGranule,
    CMAGranuleFile,
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

log = logging.getLogger(__name__)


UMM_DATE_FORMAT = "%Y-%m-%d"
UMM_DATETIME_FORMAT = f"{UMM_DATE_FORMAT}T%H:%M:%SZ"

RELATED_URL_TYPE_ORDER = ["data", "browse", "metadata", "qa", "linkage"]


class UmmgBase(ABC):
    """Abstract base class for generating a UMM-G record.

    Required UMM-G elements will either have a default implementation or have
    associated abstract methods that need to be implemented for each workflow.
    Mixin classes can be used to add boilerplate code for additional optional
    fields. Mixins will similarly define abstract methods for required UMM-G
    subelements.

    Use `get_ummg()` to generate the UMM-G record.
    """

    def __init__(self, granule: CMAGranule):
        self.now = datetime.datetime.now(timezone.utc)
        self.granule = granule

    @overload
    def date_to_str(self, date: datetime.date) -> str: ...

    @overload
    def date_to_str(self, date: None) -> None: ...

    def date_to_str(self, date: Optional[datetime.date]) -> Optional[str]:
        """Serialize a datetime.date or datetime.datetime as a string using the
        format expected by UMM-G.
        """
        if date is None:
            return None

        if isinstance(date, datetime.datetime):
            return date.strftime(self.get_umm_date_time_format())
        else:
            return date.strftime(self.get_umm_date_format())

    def get_provider_time(self) -> datetime.datetime:
        return self.now

    def get_related_urls_files(self) -> list[CMAGranuleFile]:
        return sorted(
            self.get_granule_files(),
            key=self.related_urls_files_sort_key,
        )

    def get_related_url_builder(
        self,
        file: CMAGranuleFile,
    ) -> Optional[RelatedUrlBuilder]:
        return None

    def get_related_url_type_order(self) -> list[str]:
        return RELATED_URL_TYPE_ORDER

    def get_umm_date_format(self) -> str:
        return UMM_DATE_FORMAT

    def get_umm_date_time_format(self) -> str:
        return UMM_DATETIME_FORMAT

    def related_urls_files_sort_key(self, file: CMAGranuleFile) -> tuple:
        type_order = self.get_related_url_type_order()
        try:
            type_ordinal = type_order.index(file.get("type", "data"))
        except ValueError:
            type_ordinal = len(type_order)

        return (
            type_ordinal,
            file.get("fileName"),
        )

    #
    # UMM-G elements
    #

    def get_access_constraints(self) -> Optional[AccessConstraints]:
        return None

    def get_additional_attributes(self) -> list[AdditionalAttribute]:
        return []

    def get_cloud_cover(self) -> Optional[Union[float, int]]:
        return None

    @abstractmethod
    def get_collection_reference(self) -> CollectionReference:
        pass

    def get_data_granule(self) -> Optional[DataGranule]:
        return None

    def get_granule_files(self) -> list[CMAGranuleFile]:
        return self.granule["files"]

    def get_granule_ur(self) -> str:
        return self.granule["granuleId"]

    def get_grid_mapping_names(self) -> list[str]:
        return []

    def get_input_granules(self) -> list[str]:
        return []

    def get_measured_parameters(self) -> list[MeasuredParameter]:
        return []

    def get_metadata_specification(self) -> MetadataSpecification:
        return metadata_specification("1.6.5")

    def get_native_projection_names(self) -> list[str]:
        return []

    def get_orbit_calculated_spatial_domains(
        self,
    ) -> list[OrbitCalculatedSpatialDomain]:
        return []

    def get_pge_version_class(self) -> Optional[PGEVersionClass]:
        return None

    def get_platforms(self) -> list[Platform]:
        return []

    def get_projects(self) -> list[Project]:
        return []

    def get_provider_dates(self) -> list[ProviderDate]:
        return [
            provider_date("Insert", self.date_to_str(self.get_provider_time())),
            provider_date("Update", self.date_to_str(self.get_provider_time())),
        ]

    def get_related_urls(self) -> list[RelatedUrl]:
        return [
            url
            for file in self.get_related_urls_files()
            if (builder := self.get_related_url_builder(file))
            for url in builder.get_related_urls()
        ]

    def get_spatial_extent(self) -> Optional[SpatialExtent]:
        return None

    def get_temporal_extent(self) -> Optional[TemporalExtent]:
        return None

    def get_tiling_identification_system(
        self,
    ) -> Optional[TilingIdentificationSystem]:
        return None

    def get_ummg(self) -> Ummg:
        return ummg(
            access_constraints=self.get_access_constraints(),
            additional_attributes=sorted(
                self.get_additional_attributes(),
                key=lambda attr: attr["Name"],
            )
            or None,
            cloud_cover=self.get_cloud_cover(),
            collection_reference=self.get_collection_reference(),
            data_granule=self.get_data_granule(),
            granule_ur=self.get_granule_ur(),
            grid_mapping_names=self.get_grid_mapping_names() or None,
            input_granules=self.get_input_granules() or None,
            measured_parameters=self.get_measured_parameters() or None,
            metadata_specification=self.get_metadata_specification(),
            native_projection_names=self.get_native_projection_names() or None,
            orbit_calculated_spatial_domains=(
                # ruff hint
                self.get_orbit_calculated_spatial_domains() or None
            ),
            pge_version_class=self.get_pge_version_class(),
            platforms=self.get_platforms() or None,
            projects=self.get_projects() or None,
            provider_dates=self.get_provider_dates(),
            related_urls=self.get_related_urls() or None,
            spatial_extent=self.get_spatial_extent(),
            temporal_extent=self.get_temporal_extent(),
            tiling_identification_system=self.get_tiling_identification_system(),
        )


class UmmgCollectionReferenceEntryTitleMixin(UmmgBase):
    @abstractmethod
    def get_cmr_entry_title(self) -> str:
        pass

    def get_collection_reference(self) -> CollectionReference:
        return {
            "EntryTitle": self.get_cmr_entry_title(),
        }


class UmmgCollectionReferenceShortNameVersionMixin(UmmgBase):
    @abstractmethod
    def get_cmr_short_name(self) -> str:
        pass

    @abstractmethod
    def get_cmr_version(self) -> str:
        pass

    def get_collection_reference(self) -> CollectionReference:
        return {
            "ShortName": self.get_cmr_short_name(),
            "Version": self.get_cmr_version(),
        }


class UmmgDataGranuleMixin(UmmgBase):
    """Adds a DataGranule attribute to the UMM-G"""

    def get_archive_and_distribution_information(
        self,
    ) -> list[ArchiveAndDistributionInformation]:
        return []

    def get_data_granule(self) -> DataGranule:
        return data_granule(
            archive_and_distribution_information=(
                # ruff hint
                self.get_archive_and_distribution_information() or None
            ),
            day_night_flag=self.get_day_night_flag(),
            identifiers=self.get_identifiers() or None,
            production_date_time=self.date_to_str(
                self.get_production_date_time(),
            ),
            reprocessing_actual=self.get_reprocessing_actual(),
            reprocessing_planned=self.get_reprocessing_planned(),
        )

    def get_day_night_flag(self) -> str:
        return "Unspecified"

    def get_identifiers(self) -> list[Identifier]:
        return []

    @abstractmethod
    def get_production_date_time(self) -> datetime.datetime:
        pass

    def get_reprocessing_actual(self) -> Optional[str]:
        return None

    def get_reprocessing_planned(self) -> Optional[str]:
        return None


class UmmgDataGranuleProducerGranuleIdMixin(UmmgDataGranuleMixin):
    """Includes the GranuleUR as the ProducerGranuleId in DataGranule.Identifiers"""

    def get_identifiers(self) -> list[Identifier]:
        return super().get_identifiers() + [
            identifier("ProducerGranuleId", self.get_producer_granule_id()),
        ]

    @abstractmethod
    def get_producer_granule_id(self) -> str:
        pass


class UmmgPlatformMixin(UmmgBase):
    """Adds a single Platform to the UMM-G"""

    def get_instruments(self) -> list[Instrument]:
        return []

    @abstractmethod
    def get_platform_name(self) -> str:
        pass

    def get_platforms(self) -> list[Platform]:
        return super().get_platforms() + [
            platform(
                short_name=self.get_platform_name(),
                instruments=self.get_instruments() or None,
            ),
        ]


class UmmgTemporalExtentRangeDateTimeMixin(UmmgBase):
    """Adds a TemporalExtent with RangeDateTime to the UMM-G"""

    @abstractmethod
    def get_beginning_date_time(self) -> datetime.datetime:
        pass

    def get_ending_date_time(self) -> Optional[datetime.datetime]:
        return None

    def get_temporal_extent(self) -> TemporalExtent:
        return {
            "RangeDateTime": range_date_time(
                beginning_date_time=self.date_to_str(
                    self.get_beginning_date_time(),
                ),
                ending_date_time=self.date_to_str(
                    self.get_ending_date_time(),
                ),
            ),
        }


class UmmgTemporalExtentSingleDateTimeMixin(UmmgBase):
    """Adds a TemporalExtent with SingleDateTime to the UMM-G"""

    @abstractmethod
    def get_single_date_time(self) -> datetime.datetime:
        pass

    def get_temporal_extent(self) -> TemporalExtent:
        return {
            "SingleDateTime": self.date_to_str(self.get_single_date_time()),
        }

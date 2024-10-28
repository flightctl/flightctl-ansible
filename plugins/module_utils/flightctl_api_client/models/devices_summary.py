from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.devices_summary_application_status import (
        DevicesSummaryApplicationStatus,
    )
    from ..models.devices_summary_summary_status import DevicesSummarySummaryStatus
    from ..models.devices_summary_update_status import DevicesSummaryUpdateStatus


T = TypeVar("T", bound="DevicesSummary")


@_attrs_define
class DevicesSummary:
    """A summary of the devices in the fleet returned when fetching a single Fleet.

    Attributes:
        total (int): The total number of devices in the fleet.
        application_status (DevicesSummaryApplicationStatus): A breakdown of the devices in the fleet by "application"
            status.
        summary_status (DevicesSummarySummaryStatus): A breakdown of the devices in the fleet by "summary" status.
        update_status (DevicesSummaryUpdateStatus): A breakdown of the devices in the fleet by "updated" status.
    """

    total: int
    application_status: "DevicesSummaryApplicationStatus"
    summary_status: "DevicesSummarySummaryStatus"
    update_status: "DevicesSummaryUpdateStatus"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        total = self.total

        application_status = self.application_status.to_dict()

        summary_status = self.summary_status.to_dict()

        update_status = self.update_status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total": total,
                "applicationStatus": application_status,
                "summaryStatus": summary_status,
                "updateStatus": update_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.devices_summary_application_status import (
            DevicesSummaryApplicationStatus,
        )
        from ..models.devices_summary_summary_status import DevicesSummarySummaryStatus
        from ..models.devices_summary_update_status import DevicesSummaryUpdateStatus

        d = src_dict.copy()
        total = d.pop("total")

        application_status = DevicesSummaryApplicationStatus.from_dict(
            d.pop("applicationStatus")
        )

        summary_status = DevicesSummarySummaryStatus.from_dict(d.pop("summaryStatus"))

        update_status = DevicesSummaryUpdateStatus.from_dict(d.pop("updateStatus"))

        devices_summary = cls(
            total=total,
            application_status=application_status,
            summary_status=summary_status,
            update_status=update_status,
        )

        devices_summary.additional_properties = d
        return devices_summary

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

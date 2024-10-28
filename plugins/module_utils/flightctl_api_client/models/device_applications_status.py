from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.applications_summary_status import ApplicationsSummaryStatus
    from ..models.device_applications_status_data import DeviceApplicationsStatusData


T = TypeVar("T", bound="DeviceApplicationsStatus")


@_attrs_define
class DeviceApplicationsStatus:
    """
    Attributes:
        data (DeviceApplicationsStatusData): Map of system application statuses.
        summary (ApplicationsSummaryStatus):
    """

    data: "DeviceApplicationsStatusData"
    summary: "ApplicationsSummaryStatus"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.data.to_dict()

        summary = self.summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.applications_summary_status import ApplicationsSummaryStatus
        from ..models.device_applications_status_data import (
            DeviceApplicationsStatusData,
        )

        d = src_dict.copy()
        data = DeviceApplicationsStatusData.from_dict(d.pop("data"))

        summary = ApplicationsSummaryStatus.from_dict(d.pop("summary"))

        device_applications_status = cls(
            data=data,
            summary=summary,
        )

        device_applications_status.additional_properties = d
        return device_applications_status

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

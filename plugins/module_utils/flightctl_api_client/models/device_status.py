import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.condition import Condition
    from ..models.device_application_status import DeviceApplicationStatus
    from ..models.device_applications_summary_status import (
        DeviceApplicationsSummaryStatus,
    )
    from ..models.device_config_status import DeviceConfigStatus
    from ..models.device_integrity_status import DeviceIntegrityStatus
    from ..models.device_os_status import DeviceOSStatus
    from ..models.device_resource_status import DeviceResourceStatus
    from ..models.device_summary_status import DeviceSummaryStatus
    from ..models.device_system_info import DeviceSystemInfo
    from ..models.device_updated_status import DeviceUpdatedStatus


T = TypeVar("T", bound="DeviceStatus")


@_attrs_define
class DeviceStatus:
    """DeviceStatus represents information about the status of a device. Status may trail the actual state of a device.

    Attributes:
        conditions (List['Condition']): Conditions represent the observations of a the current state of a device.
        system_info (DeviceSystemInfo): DeviceSystemInfo is a set of ids/uuids to uniquely identify the device.
        applications (List['DeviceApplicationStatus']): List of device application status.
        applications_summary (DeviceApplicationsSummaryStatus):
        resources (DeviceResourceStatus):
        integrity (DeviceIntegrityStatus):
        config (DeviceConfigStatus):
        os (DeviceOSStatus):
        updated (DeviceUpdatedStatus):
        summary (DeviceSummaryStatus):
        last_seen (datetime.datetime):
    """

    conditions: List["Condition"]
    system_info: "DeviceSystemInfo"
    applications: List["DeviceApplicationStatus"]
    applications_summary: "DeviceApplicationsSummaryStatus"
    resources: "DeviceResourceStatus"
    integrity: "DeviceIntegrityStatus"
    config: "DeviceConfigStatus"
    os: "DeviceOSStatus"
    updated: "DeviceUpdatedStatus"
    summary: "DeviceSummaryStatus"
    last_seen: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        system_info = self.system_info.to_dict()

        applications = []
        for applications_item_data in self.applications:
            applications_item = applications_item_data.to_dict()
            applications.append(applications_item)

        applications_summary = self.applications_summary.to_dict()

        resources = self.resources.to_dict()

        integrity = self.integrity.to_dict()

        config = self.config.to_dict()

        os = self.os.to_dict()

        updated = self.updated.to_dict()

        summary = self.summary.to_dict()

        last_seen = self.last_seen.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
                "systemInfo": system_info,
                "applications": applications,
                "applicationsSummary": applications_summary,
                "resources": resources,
                "integrity": integrity,
                "config": config,
                "os": os,
                "updated": updated,
                "summary": summary,
                "lastSeen": last_seen,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.condition import Condition
        from ..models.device_application_status import DeviceApplicationStatus
        from ..models.device_applications_summary_status import (
            DeviceApplicationsSummaryStatus,
        )
        from ..models.device_config_status import DeviceConfigStatus
        from ..models.device_integrity_status import DeviceIntegrityStatus
        from ..models.device_os_status import DeviceOSStatus
        from ..models.device_resource_status import DeviceResourceStatus
        from ..models.device_summary_status import DeviceSummaryStatus
        from ..models.device_system_info import DeviceSystemInfo
        from ..models.device_updated_status import DeviceUpdatedStatus

        d = src_dict.copy()
        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = Condition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        system_info = DeviceSystemInfo.from_dict(d.pop("systemInfo"))

        applications = []
        _applications = d.pop("applications")
        for applications_item_data in _applications:
            applications_item = DeviceApplicationStatus.from_dict(
                applications_item_data
            )

            applications.append(applications_item)

        applications_summary = DeviceApplicationsSummaryStatus.from_dict(
            d.pop("applicationsSummary")
        )

        resources = DeviceResourceStatus.from_dict(d.pop("resources"))

        integrity = DeviceIntegrityStatus.from_dict(d.pop("integrity"))

        config = DeviceConfigStatus.from_dict(d.pop("config"))

        os = DeviceOSStatus.from_dict(d.pop("os"))

        updated = DeviceUpdatedStatus.from_dict(d.pop("updated"))

        summary = DeviceSummaryStatus.from_dict(d.pop("summary"))

        last_seen = isoparse(d.pop("lastSeen"))

        device_status = cls(
            conditions=conditions,
            system_info=system_info,
            applications=applications,
            applications_summary=applications_summary,
            resources=resources,
            integrity=integrity,
            config=config,
            os=os,
            updated=updated,
            summary=summary,
            last_seen=last_seen,
        )

        device_status.additional_properties = d
        return device_status

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

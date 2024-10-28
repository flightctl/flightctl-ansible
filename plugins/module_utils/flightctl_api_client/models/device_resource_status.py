from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_resource_status_type import (
    DeviceResourceStatusType,
    check_device_resource_status_type,
)

T = TypeVar("T", bound="DeviceResourceStatus")


@_attrs_define
class DeviceResourceStatus:
    """
    Attributes:
        cpu (DeviceResourceStatusType):
        memory (DeviceResourceStatusType):
        disk (DeviceResourceStatusType):
    """

    cpu: DeviceResourceStatusType
    memory: DeviceResourceStatusType
    disk: DeviceResourceStatusType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        cpu: str = self.cpu

        memory: str = self.memory

        disk: str = self.disk

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cpu": cpu,
                "memory": memory,
                "disk": disk,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        cpu = check_device_resource_status_type(d.pop("cpu"))

        memory = check_device_resource_status_type(d.pop("memory"))

        disk = check_device_resource_status_type(d.pop("disk"))

        device_resource_status = cls(
            cpu=cpu,
            memory=memory,
            disk=disk,
        )

        device_resource_status.additional_properties = d
        return device_resource_status

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

from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceSystemInfo")


@_attrs_define
class DeviceSystemInfo:
    """DeviceSystemInfo is a set of ids/uuids to uniquely identify the device.

    Attributes:
        architecture (str): The Architecture reported by the device.
        boot_id (str): Boot ID reported by the device.
        operating_system (str): The Operating System reported by the device.
    """

    architecture: str
    boot_id: str
    operating_system: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        architecture = self.architecture

        boot_id = self.boot_id

        operating_system = self.operating_system

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "architecture": architecture,
                "bootID": boot_id,
                "operatingSystem": operating_system,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        architecture = d.pop("architecture")

        boot_id = d.pop("bootID")

        operating_system = d.pop("operatingSystem")

        device_system_info = cls(
            architecture=architecture,
            boot_id=boot_id,
            operating_system=operating_system,
        )

        device_system_info.additional_properties = d
        return device_system_info

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

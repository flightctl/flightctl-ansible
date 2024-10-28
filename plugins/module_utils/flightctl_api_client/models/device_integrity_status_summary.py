from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.device_integrity_status_summary_type import (
    DeviceIntegrityStatusSummaryType,
    check_device_integrity_status_summary_type,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="DeviceIntegrityStatusSummary")


@_attrs_define
class DeviceIntegrityStatusSummary:
    """
    Attributes:
        status (DeviceIntegrityStatusSummaryType):
        info (Union[Unset, str]): Human readable information about the last integrity transition.
    """

    status: DeviceIntegrityStatusSummaryType
    info: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        status: str = self.status

        info = self.info

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if info is not UNSET:
            field_dict["info"] = info

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        status = check_device_integrity_status_summary_type(d.pop("status"))

        info = d.pop("info", UNSET)

        device_integrity_status_summary = cls(
            status=status,
            info=info,
        )

        device_integrity_status_summary.additional_properties = d
        return device_integrity_status_summary

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

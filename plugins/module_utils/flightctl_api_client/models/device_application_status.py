from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.application_status_type import (
    ApplicationStatusType,
    check_application_status_type,
)

T = TypeVar("T", bound="DeviceApplicationStatus")


@_attrs_define
class DeviceApplicationStatus:
    """
    Attributes:
        name (str): Human readable name of the application.
        ready (str): The number of containers which are ready in the application.
        restarts (int): Number of restarts observed for the application.
        status (ApplicationStatusType):
    """

    name: str
    ready: str
    restarts: int
    status: ApplicationStatusType
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        ready = self.ready

        restarts = self.restarts

        status: str = self.status

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "ready": ready,
                "restarts": restarts,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        ready = d.pop("ready")

        restarts = d.pop("restarts")

        status = check_application_status_type(d.pop("status"))

        device_application_status = cls(
            name=name,
            ready=ready,
            restarts=restarts,
            status=status,
        )

        device_application_status.additional_properties = d
        return device_application_status

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

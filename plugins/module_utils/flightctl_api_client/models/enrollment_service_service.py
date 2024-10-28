from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnrollmentServiceService")


@_attrs_define
class EnrollmentServiceService:
    """
    Attributes:
        certificate_authority_data (str):
        server (str):
    """

    certificate_authority_data: str
    server: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        certificate_authority_data = self.certificate_authority_data

        server = self.server

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "certificate-authority-data": certificate_authority_data,
                "server": server,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        certificate_authority_data = d.pop("certificate-authority-data")

        server = d.pop("server")

        enrollment_service_service = cls(
            certificate_authority_data=certificate_authority_data,
            server=server,
        )

        enrollment_service_service.additional_properties = d
        return enrollment_service_service

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

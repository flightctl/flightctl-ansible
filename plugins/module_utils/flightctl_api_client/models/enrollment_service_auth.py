from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EnrollmentServiceAuth")


@_attrs_define
class EnrollmentServiceAuth:
    """
    Attributes:
        client_certificate_data (str):
        client_key_data (str):
    """

    client_certificate_data: str
    client_key_data: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        client_certificate_data = self.client_certificate_data

        client_key_data = self.client_key_data

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "client-certificate-data": client_certificate_data,
                "client-key-data": client_key_data,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        client_certificate_data = d.pop("client-certificate-data")

        client_key_data = d.pop("client-key-data")

        enrollment_service_auth = cls(
            client_certificate_data=client_certificate_data,
            client_key_data=client_key_data,
        )

        enrollment_service_auth.additional_properties = d
        return enrollment_service_auth

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

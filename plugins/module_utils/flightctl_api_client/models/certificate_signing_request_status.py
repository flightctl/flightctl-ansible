from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.condition import Condition


T = TypeVar("T", bound="CertificateSigningRequestStatus")


@_attrs_define
class CertificateSigningRequestStatus:
    """Indicates approval/denial/failure status of the CSR, and contains the issued certifiate if any exists

    Attributes:
        conditions (List['Condition']): Conditions applied to the request. Known conditions are Approved, Denied, and
            Failed
        certificate (Union[Unset, str]): The issued signed certificate, immutable once populated
    """

    conditions: List["Condition"]
    certificate: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        certificate = self.certificate

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
            }
        )
        if certificate is not UNSET:
            field_dict["certificate"] = certificate

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.condition import Condition

        d = src_dict.copy()
        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = Condition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        certificate = d.pop("certificate", UNSET)

        certificate_signing_request_status = cls(
            conditions=conditions,
            certificate=certificate,
        )

        certificate_signing_request_status.additional_properties = d
        return certificate_signing_request_status

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

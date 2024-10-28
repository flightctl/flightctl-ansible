from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.condition import Condition
    from ..models.enrollment_request_approval import EnrollmentRequestApproval


T = TypeVar("T", bound="EnrollmentRequestStatus")


@_attrs_define
class EnrollmentRequestStatus:
    """EnrollmentRequestStatus represents information about the status of a EnrollmentRequest.

    Attributes:
        conditions (List['Condition']): Current state of the EnrollmentRequest.
        certificate (Union[Unset, str]): certificate is a PEM-encoded signed certificate.
        approval (Union[Unset, EnrollmentRequestApproval]):
    """

    conditions: List["Condition"]
    certificate: Union[Unset, str] = UNSET
    approval: Union[Unset, "EnrollmentRequestApproval"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        certificate = self.certificate

        approval: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.approval, Unset):
            approval = self.approval.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
            }
        )
        if certificate is not UNSET:
            field_dict["certificate"] = certificate
        if approval is not UNSET:
            field_dict["approval"] = approval

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.condition import Condition
        from ..models.enrollment_request_approval import EnrollmentRequestApproval

        d = src_dict.copy()
        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = Condition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        certificate = d.pop("certificate", UNSET)

        _approval = d.pop("approval", UNSET)
        approval: Union[Unset, EnrollmentRequestApproval]
        if isinstance(_approval, Unset):
            approval = UNSET
        else:
            approval = EnrollmentRequestApproval.from_dict(_approval)

        enrollment_request_status = cls(
            conditions=conditions,
            certificate=certificate,
            approval=approval,
        )

        enrollment_request_status.additional_properties = d
        return enrollment_request_status

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

from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Status")


@_attrs_define
class Status:
    """Status is a return value for calls that don't return other objects.

    Attributes:
        message (Union[Unset, str]): A human-readable description of the status of this operation.
        reason (Union[Unset, str]): A machine-readable description of why this operation is in the "Failure" status. If
            this value is empty there is no information available. A Reason clarifies an HTTP status code but does not
            override it.
        status (Union[Unset, str]): Status of the operation. One of: "Success" or "Failure". More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#spec-and-status
    """

    message: Union[Unset, str] = UNSET
    reason: Union[Unset, str] = UNSET
    status: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        message = self.message

        reason = self.reason

        status = self.status

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message is not UNSET:
            field_dict["message"] = message
        if reason is not UNSET:
            field_dict["reason"] = reason
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        message = d.pop("message", UNSET)

        reason = d.pop("reason", UNSET)

        status = d.pop("status", UNSET)

        status = cls(
            message=message,
            reason=reason,
            status=status,
        )

        status.additional_properties = d
        return status

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

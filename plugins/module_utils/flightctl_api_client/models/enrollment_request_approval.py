import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.enrollment_request_approval_labels import (
        EnrollmentRequestApprovalLabels,
    )


T = TypeVar("T", bound="EnrollmentRequestApproval")


@_attrs_define
class EnrollmentRequestApproval:
    """
    Attributes:
        approved (bool): approved indicates whether the request has been approved.
        labels (Union[Unset, EnrollmentRequestApprovalLabels]): labels is a set of labels to apply to the device.
        approved_by (Union[Unset, str]): approvedBy is the name of the approver.
        approved_at (Union[Unset, datetime.datetime]): approvedAt is the time at which the request was approved.
    """

    approved: bool
    labels: Union[Unset, "EnrollmentRequestApprovalLabels"] = UNSET
    approved_by: Union[Unset, str] = UNSET
    approved_at: Union[Unset, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        approved = self.approved

        labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        approved_by = self.approved_by

        approved_at: Union[Unset, str] = UNSET
        if not isinstance(self.approved_at, Unset):
            approved_at = self.approved_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "approved": approved,
            }
        )
        if labels is not UNSET:
            field_dict["labels"] = labels
        if approved_by is not UNSET:
            field_dict["approvedBy"] = approved_by
        if approved_at is not UNSET:
            field_dict["approvedAt"] = approved_at

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.enrollment_request_approval_labels import (
            EnrollmentRequestApprovalLabels,
        )

        d = src_dict.copy()
        approved = d.pop("approved")

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, EnrollmentRequestApprovalLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = EnrollmentRequestApprovalLabels.from_dict(_labels)

        approved_by = d.pop("approvedBy", UNSET)

        _approved_at = d.pop("approvedAt", UNSET)
        approved_at: Union[Unset, datetime.datetime]
        if isinstance(_approved_at, Unset):
            approved_at = UNSET
        else:
            approved_at = isoparse(_approved_at)

        enrollment_request_approval = cls(
            approved=approved,
            labels=labels,
            approved_by=approved_by,
            approved_at=approved_at,
        )

        enrollment_request_approval.additional_properties = d
        return enrollment_request_approval

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

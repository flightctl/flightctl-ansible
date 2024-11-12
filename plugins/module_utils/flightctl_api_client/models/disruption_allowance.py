from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DisruptionAllowance")


@_attrs_define
class DisruptionAllowance:
    """DisruptionAllowance defines the level of allowed disruption when rollout is in progress.

    Attributes:
        group_by (Union[Unset, List[str]]): List of label keys to perform grouping for the disruption allowance.
        min_available (Union[Unset, int]): The maximum number of unavailable devices allowed during rollout.
        max_unavailable (Union[Unset, int]): The minimum number of required available devices during rollout.
    """

    group_by: Union[Unset, List[str]] = UNSET
    min_available: Union[Unset, int] = UNSET
    max_unavailable: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        group_by: Union[Unset, List[str]] = UNSET
        if not isinstance(self.group_by, Unset):
            group_by = self.group_by

        min_available = self.min_available

        max_unavailable = self.max_unavailable

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group_by is not UNSET:
            field_dict["groupBy"] = group_by
        if min_available is not UNSET:
            field_dict["minAvailable"] = min_available
        if max_unavailable is not UNSET:
            field_dict["maxUnavailable"] = max_unavailable

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        group_by = cast(List[str], d.pop("groupBy", UNSET))

        min_available = d.pop("minAvailable", UNSET)

        max_unavailable = d.pop("maxUnavailable", UNSET)

        disruption_allowance = cls(
            group_by=group_by,
            min_available=min_available,
            max_unavailable=max_unavailable,
        )

        disruption_allowance.additional_properties = d
        return disruption_allowance

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

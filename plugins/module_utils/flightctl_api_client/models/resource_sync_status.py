from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.condition import Condition


T = TypeVar("T", bound="ResourceSyncStatus")


@_attrs_define
class ResourceSyncStatus:
    """ResourceSyncStatus represents information about the status of a resourcesync

    Attributes:
        conditions (List['Condition']): Current state of a resourcesync.
        observed_commit (Union[Unset, str]): The last commit hash that was synced
        observed_generation (Union[Unset, int]): The last generation that was synced
    """

    conditions: List["Condition"]
    observed_commit: Union[Unset, str] = UNSET
    observed_generation: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        observed_commit = self.observed_commit

        observed_generation = self.observed_generation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
            }
        )
        if observed_commit is not UNSET:
            field_dict["observedCommit"] = observed_commit
        if observed_generation is not UNSET:
            field_dict["observedGeneration"] = observed_generation

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

        observed_commit = d.pop("observedCommit", UNSET)

        observed_generation = d.pop("observedGeneration", UNSET)

        resource_sync_status = cls(
            conditions=conditions,
            observed_commit=observed_commit,
            observed_generation=observed_generation,
        )

        resource_sync_status.additional_properties = d
        return resource_sync_status

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

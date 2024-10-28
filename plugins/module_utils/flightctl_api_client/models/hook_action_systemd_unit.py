from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.hook_action_systemd_unit_operations_item import (
    HookActionSystemdUnitOperationsItem,
    check_hook_action_systemd_unit_operations_item,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="HookActionSystemdUnit")


@_attrs_define
class HookActionSystemdUnit:
    """
    Attributes:
        name (str): The name of the systemd unit on which the specified operations will be performed. This should be the
            exact name of the unit file, such as example.service. If the name is not populated the name will be auto
            discovered from the file path.
        operations (List[HookActionSystemdUnitOperationsItem]): The specific systemd operations to perform on the
            specified unit.
        work_dir (Union[Unset, str]): The directory in which the executable will be run from if it is left empty it will
            run from the users home directory.
    """

    name: str
    operations: List[HookActionSystemdUnitOperationsItem]
    work_dir: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        operations = []
        for operations_item_data in self.operations:
            operations_item: str = operations_item_data
            operations.append(operations_item)

        work_dir = self.work_dir

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "operations": operations,
            }
        )
        if work_dir is not UNSET:
            field_dict["workDir"] = work_dir

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        operations = []
        _operations = d.pop("operations")
        for operations_item_data in _operations:
            operations_item = check_hook_action_systemd_unit_operations_item(
                operations_item_data
            )

            operations.append(operations_item)

        work_dir = d.pop("workDir", UNSET)

        hook_action_systemd_unit = cls(
            name=name,
            operations=operations,
            work_dir=work_dir,
        )

        hook_action_systemd_unit.additional_properties = d
        return hook_action_systemd_unit

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

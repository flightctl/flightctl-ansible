from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.file_operation import FileOperation, check_file_operation
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hook_action_type_0 import HookActionType0
    from ..models.hook_action_type_1 import HookActionType1


T = TypeVar("T", bound="DeviceUpdateHookSpec")


@_attrs_define
class DeviceUpdateHookSpec:
    """
    Attributes:
        actions (List[Union['HookActionType0', 'HookActionType1']]): The actions to take when the specified file
            operations are observed. Each action is executed in the order they are defined.
        name (Union[Unset, str]):
        description (Union[Unset, str]):
        on_file (Union[Unset, List[FileOperation]]):
        path (Union[Unset, str]): The path to monitor for changes in configuration files. This path can point to either
            a specific file or an entire directory.
    """

    actions: List[Union["HookActionType0", "HookActionType1"]]
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    on_file: Union[Unset, List[FileOperation]] = UNSET
    path: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.hook_action_type_0 import HookActionType0

        actions = []
        for actions_item_data in self.actions:
            actions_item: Dict[str, Any]
            if isinstance(actions_item_data, HookActionType0):
                actions_item = actions_item_data.to_dict()
            else:
                actions_item = actions_item_data.to_dict()

            actions.append(actions_item)

        name = self.name

        description = self.description

        on_file: Union[Unset, List[str]] = UNSET
        if not isinstance(self.on_file, Unset):
            on_file = []
            for on_file_item_data in self.on_file:
                on_file_item: str = on_file_item_data
                on_file.append(on_file_item)

        path = self.path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actions": actions,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if on_file is not UNSET:
            field_dict["onFile"] = on_file
        if path is not UNSET:
            field_dict["path"] = path

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hook_action_type_0 import HookActionType0
        from ..models.hook_action_type_1 import HookActionType1

        d = src_dict.copy()
        actions = []
        _actions = d.pop("actions")
        for actions_item_data in _actions:

            def _parse_actions_item(
                data: object,
            ) -> Union["HookActionType0", "HookActionType1"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_hook_action_type_0 = HookActionType0.from_dict(
                        data
                    )

                    return componentsschemas_hook_action_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_hook_action_type_1 = HookActionType1.from_dict(data)

                return componentsschemas_hook_action_type_1

            actions_item = _parse_actions_item(actions_item_data)

            actions.append(actions_item)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        on_file = []
        _on_file = d.pop("onFile", UNSET)
        for on_file_item_data in _on_file or []:
            on_file_item = check_file_operation(on_file_item_data)

            on_file.append(on_file_item)

        path = d.pop("path", UNSET)

        device_update_hook_spec = cls(
            actions=actions,
            name=name,
            description=description,
            on_file=on_file,
            path=path,
        )

        device_update_hook_spec.additional_properties = d
        return device_update_hook_spec

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

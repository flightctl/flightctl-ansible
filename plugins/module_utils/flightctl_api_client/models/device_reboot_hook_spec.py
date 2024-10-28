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

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hook_action_type_0 import HookActionType0
    from ..models.hook_action_type_1 import HookActionType1


T = TypeVar("T", bound="DeviceRebootHookSpec")


@_attrs_define
class DeviceRebootHookSpec:
    """
    Attributes:
        actions (List[Union['HookActionType0', 'HookActionType1']]): The actions taken before and after system reboots
            are observed. Each action is executed in the order they are defined.
        name (Union[Unset, str]):
        description (Union[Unset, str]):
    """

    actions: List[Union["HookActionType0", "HookActionType1"]]
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
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

        device_reboot_hook_spec = cls(
            actions=actions,
            name=name,
            description=description,
        )

        device_reboot_hook_spec.additional_properties = d
        return device_reboot_hook_spec

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

from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_reboot_hook_spec import DeviceRebootHookSpec
    from ..models.device_update_hook_spec import DeviceUpdateHookSpec


T = TypeVar("T", bound="DeviceHooksSpec")


@_attrs_define
class DeviceHooksSpec:
    """
    Attributes:
        before_updating (Union[Unset, List['DeviceUpdateHookSpec']]): Hooks executed before updating allow for custom
            actions and integration with other systems
            or services. These actions occur before configuration changes are applied to the device.
        after_updating (Union[Unset, List['DeviceUpdateHookSpec']]): Hooks executed after updating enable custom actions
            and integration with other systems
            or services. These actions occur after configuration changes have been applied to the device.
        before_rebooting (Union[Unset, List['DeviceRebootHookSpec']]): Hooks executed before rebooting allow for custom
            actions and integration with other systems
            or services. These actions occur before the device is rebooted.
        after_rebooting (Union[Unset, List['DeviceRebootHookSpec']]): Hooks executed after rebooting enable custom
            actions and integration with other systems
            or services. These actions occur after the device has rebooted, allowing for post-reboot tasks.
    """

    before_updating: Union[Unset, List["DeviceUpdateHookSpec"]] = UNSET
    after_updating: Union[Unset, List["DeviceUpdateHookSpec"]] = UNSET
    before_rebooting: Union[Unset, List["DeviceRebootHookSpec"]] = UNSET
    after_rebooting: Union[Unset, List["DeviceRebootHookSpec"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        before_updating: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.before_updating, Unset):
            before_updating = []
            for before_updating_item_data in self.before_updating:
                before_updating_item = before_updating_item_data.to_dict()
                before_updating.append(before_updating_item)

        after_updating: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.after_updating, Unset):
            after_updating = []
            for after_updating_item_data in self.after_updating:
                after_updating_item = after_updating_item_data.to_dict()
                after_updating.append(after_updating_item)

        before_rebooting: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.before_rebooting, Unset):
            before_rebooting = []
            for before_rebooting_item_data in self.before_rebooting:
                before_rebooting_item = before_rebooting_item_data.to_dict()
                before_rebooting.append(before_rebooting_item)

        after_rebooting: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.after_rebooting, Unset):
            after_rebooting = []
            for after_rebooting_item_data in self.after_rebooting:
                after_rebooting_item = after_rebooting_item_data.to_dict()
                after_rebooting.append(after_rebooting_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if before_updating is not UNSET:
            field_dict["beforeUpdating"] = before_updating
        if after_updating is not UNSET:
            field_dict["afterUpdating"] = after_updating
        if before_rebooting is not UNSET:
            field_dict["beforeRebooting"] = before_rebooting
        if after_rebooting is not UNSET:
            field_dict["afterRebooting"] = after_rebooting

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device_reboot_hook_spec import DeviceRebootHookSpec
        from ..models.device_update_hook_spec import DeviceUpdateHookSpec

        d = src_dict.copy()
        before_updating = []
        _before_updating = d.pop("beforeUpdating", UNSET)
        for before_updating_item_data in _before_updating or []:
            before_updating_item = DeviceUpdateHookSpec.from_dict(
                before_updating_item_data
            )

            before_updating.append(before_updating_item)

        after_updating = []
        _after_updating = d.pop("afterUpdating", UNSET)
        for after_updating_item_data in _after_updating or []:
            after_updating_item = DeviceUpdateHookSpec.from_dict(
                after_updating_item_data
            )

            after_updating.append(after_updating_item)

        before_rebooting = []
        _before_rebooting = d.pop("beforeRebooting", UNSET)
        for before_rebooting_item_data in _before_rebooting or []:
            before_rebooting_item = DeviceRebootHookSpec.from_dict(
                before_rebooting_item_data
            )

            before_rebooting.append(before_rebooting_item)

        after_rebooting = []
        _after_rebooting = d.pop("afterRebooting", UNSET)
        for after_rebooting_item_data in _after_rebooting or []:
            after_rebooting_item = DeviceRebootHookSpec.from_dict(
                after_rebooting_item_data
            )

            after_rebooting.append(after_rebooting_item)

        device_hooks_spec = cls(
            before_updating=before_updating,
            after_updating=after_updating,
            before_rebooting=before_rebooting,
            after_rebooting=after_rebooting,
        )

        device_hooks_spec.additional_properties = d
        return device_hooks_spec

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

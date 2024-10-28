from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.hook_action_systemd_unit import HookActionSystemdUnit


T = TypeVar("T", bound="HookActionSystemdSpec")


@_attrs_define
class HookActionSystemdSpec:
    """
    Attributes:
        unit (HookActionSystemdUnit):
        timeout (Union[Unset, str]): The maximum duration allowed for the action to complete.
            The duration should be specified as a positive integer
            followed by a time unit. Supported time units are:
            - 's' for seconds
            - 'm' for minutes
            - 'h' for hours
            - 'd' for days
    """

    unit: "HookActionSystemdUnit"
    timeout: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        unit = self.unit.to_dict()

        timeout = self.timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "unit": unit,
            }
        )
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hook_action_systemd_unit import HookActionSystemdUnit

        d = src_dict.copy()
        unit = HookActionSystemdUnit.from_dict(d.pop("unit"))

        timeout = d.pop("timeout", UNSET)

        hook_action_systemd_spec = cls(
            unit=unit,
            timeout=timeout,
        )

        hook_action_systemd_spec.additional_properties = d
        return hook_action_systemd_spec

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

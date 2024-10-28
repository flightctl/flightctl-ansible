from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HookActionSpec")


@_attrs_define
class HookActionSpec:
    """
    Attributes:
        timeout (Union[Unset, str]): The maximum duration allowed for the action to complete.
            The duration should be specified as a positive integer
            followed by a time unit. Supported time units are:
            - 's' for seconds
            - 'm' for minutes
            - 'h' for hours
            - 'd' for days
    """

    timeout: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        timeout = self.timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timeout is not UNSET:
            field_dict["timeout"] = timeout

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        timeout = d.pop("timeout", UNSET)

        hook_action_spec = cls(
            timeout=timeout,
        )

        hook_action_spec.additional_properties = d
        return hook_action_spec

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

from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.hook_action_executable_spec import HookActionExecutableSpec


T = TypeVar("T", bound="HookActionType0")


@_attrs_define
class HookActionType0:
    """
    Attributes:
        executable (HookActionExecutableSpec):
    """

    executable: "HookActionExecutableSpec"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        executable = self.executable.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "executable": executable,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.hook_action_executable_spec import HookActionExecutableSpec

        d = src_dict.copy()
        executable = HookActionExecutableSpec.from_dict(d.pop("executable"))

        hook_action_type_0 = cls(
            executable=executable,
        )

        hook_action_type_0.additional_properties = d
        return hook_action_type_0

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

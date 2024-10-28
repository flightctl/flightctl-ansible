from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.file_spec import FileSpec


T = TypeVar("T", bound="InlineConfigProviderSpec")


@_attrs_define
class InlineConfigProviderSpec:
    """
    Attributes:
        config_type (str):
        name (str):
        inline (List['FileSpec']):
    """

    config_type: str
    name: str
    inline: List["FileSpec"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config_type = self.config_type

        name = self.name

        inline = []
        for inline_item_data in self.inline:
            inline_item = inline_item_data.to_dict()
            inline.append(inline_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configType": config_type,
                "name": name,
                "inline": inline,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.file_spec import FileSpec

        d = src_dict.copy()
        config_type = d.pop("configType")

        name = d.pop("name")

        inline = []
        _inline = d.pop("inline")
        for inline_item_data in _inline:
            inline_item = FileSpec.from_dict(inline_item_data)

            inline.append(inline_item)

        inline_config_provider_spec = cls(
            config_type=config_type,
            name=name,
            inline=inline,
        )

        inline_config_provider_spec.additional_properties = d
        return inline_config_provider_spec

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

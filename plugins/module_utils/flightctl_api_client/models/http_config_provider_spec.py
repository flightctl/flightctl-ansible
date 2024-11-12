from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.http_config_provider_spec_http_ref import (
        HttpConfigProviderSpecHttpRef,
    )


T = TypeVar("T", bound="HttpConfigProviderSpec")


@_attrs_define
class HttpConfigProviderSpec:
    """
    Attributes:
        name (str): The name of the config provider
        http_ref (HttpConfigProviderSpecHttpRef):
    """

    name: str
    http_ref: "HttpConfigProviderSpecHttpRef"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        http_ref = self.http_ref.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "httpRef": http_ref,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.http_config_provider_spec_http_ref import (
            HttpConfigProviderSpecHttpRef,
        )

        d = src_dict.copy()
        name = d.pop("name")

        http_ref = HttpConfigProviderSpecHttpRef.from_dict(d.pop("httpRef"))

        http_config_provider_spec = cls(
            name=name,
            http_ref=http_ref,
        )

        http_config_provider_spec.additional_properties = d
        return http_config_provider_spec

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

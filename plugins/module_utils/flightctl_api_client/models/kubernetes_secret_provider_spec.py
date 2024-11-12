from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.kubernetes_secret_provider_spec_secret_ref import (
        KubernetesSecretProviderSpecSecretRef,
    )


T = TypeVar("T", bound="KubernetesSecretProviderSpec")


@_attrs_define
class KubernetesSecretProviderSpec:
    """
    Attributes:
        name (str): The name of the config provider
        secret_ref (KubernetesSecretProviderSpecSecretRef):
    """

    name: str
    secret_ref: "KubernetesSecretProviderSpecSecretRef"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        secret_ref = self.secret_ref.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "secretRef": secret_ref,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.kubernetes_secret_provider_spec_secret_ref import (
            KubernetesSecretProviderSpecSecretRef,
        )

        d = src_dict.copy()
        name = d.pop("name")

        secret_ref = KubernetesSecretProviderSpecSecretRef.from_dict(d.pop("secretRef"))

        kubernetes_secret_provider_spec = cls(
            name=name,
            secret_ref=secret_ref,
        )

        kubernetes_secret_provider_spec.additional_properties = d
        return kubernetes_secret_provider_spec

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

from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="KubernetesSecretProviderSpecSecretRef")


@_attrs_define
class KubernetesSecretProviderSpecSecretRef:
    """
    Attributes:
        name (str):
        namespace (str):
        mount_path (str):
    """

    name: str
    namespace: str
    mount_path: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        namespace = self.namespace

        mount_path = self.mount_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "namespace": namespace,
                "mountPath": mount_path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        namespace = d.pop("namespace")

        mount_path = d.pop("mountPath")

        kubernetes_secret_provider_spec_secret_ref = cls(
            name=name,
            namespace=namespace,
            mount_path=mount_path,
        )

        kubernetes_secret_provider_spec_secret_ref.additional_properties = d
        return kubernetes_secret_provider_spec_secret_ref

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

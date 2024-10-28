from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResourceSyncSpec")


@_attrs_define
class ResourceSyncSpec:
    """
    Attributes:
        repository (str): The name of the repository resource to use as the sync source
        target_revision (str): The desired revision in the repository
        path (str): The path of a file or directory in the repository. If a directory,
            the directory should contain only resource definitions with no
            subdirectories. Each file should contain the definition of one or
            more resources.
    """

    repository: str
    target_revision: str
    path: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        repository = self.repository

        target_revision = self.target_revision

        path = self.path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository": repository,
                "targetRevision": target_revision,
                "path": path,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        repository = d.pop("repository")

        target_revision = d.pop("targetRevision")

        path = d.pop("path")

        resource_sync_spec = cls(
            repository=repository,
            target_revision=target_revision,
            path=path,
        )

        resource_sync_spec.additional_properties = d
        return resource_sync_spec

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

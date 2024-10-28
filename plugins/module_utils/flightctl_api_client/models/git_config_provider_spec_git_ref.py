from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GitConfigProviderSpecGitRef")


@_attrs_define
class GitConfigProviderSpecGitRef:
    """
    Attributes:
        repository (str): The name of the repository resource to use as the sync source
        target_revision (str):
        path (str):
        mount_path (Union[Unset, str]): Path to config in device Default: '/'.
    """

    repository: str
    target_revision: str
    path: str
    mount_path: Union[Unset, str] = "/"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        repository = self.repository

        target_revision = self.target_revision

        path = self.path

        mount_path = self.mount_path

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository": repository,
                "targetRevision": target_revision,
                "path": path,
            }
        )
        if mount_path is not UNSET:
            field_dict["mountPath"] = mount_path

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        repository = d.pop("repository")

        target_revision = d.pop("targetRevision")

        path = d.pop("path")

        mount_path = d.pop("mountPath", UNSET)

        git_config_provider_spec_git_ref = cls(
            repository=repository,
            target_revision=target_revision,
            path=path,
            mount_path=mount_path,
        )

        git_config_provider_spec_git_ref.additional_properties = d
        return git_config_provider_spec_git_ref

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

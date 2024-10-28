from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.git_config_provider_spec_git_ref import GitConfigProviderSpecGitRef


T = TypeVar("T", bound="GitConfigProviderSpec")


@_attrs_define
class GitConfigProviderSpec:
    """
    Attributes:
        config_type (str):
        name (str):
        git_ref (GitConfigProviderSpecGitRef):
    """

    config_type: str
    name: str
    git_ref: "GitConfigProviderSpecGitRef"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        config_type = self.config_type

        name = self.name

        git_ref = self.git_ref.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "configType": config_type,
                "name": name,
                "gitRef": git_ref,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.git_config_provider_spec_git_ref import (
            GitConfigProviderSpecGitRef,
        )

        d = src_dict.copy()
        config_type = d.pop("configType")

        name = d.pop("name")

        git_ref = GitConfigProviderSpecGitRef.from_dict(d.pop("gitRef"))

        git_config_provider_spec = cls(
            config_type=config_type,
            name=name,
            git_ref=git_ref,
        )

        git_config_provider_spec.additional_properties = d
        return git_config_provider_spec

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

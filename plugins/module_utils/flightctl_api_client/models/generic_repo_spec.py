from typing import Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.repo_spec_type import RepoSpecType, check_repo_spec_type

T = TypeVar("T", bound="GenericRepoSpec")


@_attrs_define
class GenericRepoSpec:
    """
    Attributes:
        url (str): The (possibly remote) repository URL
        type (RepoSpecType): RepoSpecType is the type of the repository
    """

    url: str
    type: RepoSpecType

    def to_dict(self) -> Dict[str, Any]:
        url = self.url

        type: str = self.type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "url": url,
                "type": type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        url = d.pop("url")

        type = check_repo_spec_type(d.pop("type"))

        generic_repo_spec = cls(
            url=url,
            type=type,
        )

        return generic_repo_spec

from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.repo_spec_type import RepoSpecType, check_repo_spec_type

if TYPE_CHECKING:
    from ..models.ssh_config import SshConfig


T = TypeVar("T", bound="SshRepoSpec")


@_attrs_define
class SshRepoSpec:
    """
    Attributes:
        url (str): The SSH Git repository URL to clone from
        type (RepoSpecType): RepoSpecType is the type of the repository
        ssh_config (SshConfig):
    """

    url: str
    type: RepoSpecType
    ssh_config: "SshConfig"

    def to_dict(self) -> Dict[str, Any]:
        url = self.url

        type: str = self.type

        ssh_config = self.ssh_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "url": url,
                "type": type,
                "sshConfig": ssh_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.ssh_config import SshConfig

        d = src_dict.copy()
        url = d.pop("url")

        type = check_repo_spec_type(d.pop("type"))

        ssh_config = SshConfig.from_dict(d.pop("sshConfig"))

        ssh_repo_spec = cls(
            url=url,
            type=type,
            ssh_config=ssh_config,
        )

        return ssh_repo_spec

from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar

from attrs import define as _attrs_define

from ..models.repo_spec_type import RepoSpecType, check_repo_spec_type

if TYPE_CHECKING:
    from ..models.http_config import HttpConfig


T = TypeVar("T", bound="HttpRepoSpec")


@_attrs_define
class HttpRepoSpec:
    """
    Attributes:
        url (str): The HTTP URL to call or clone from
        type (RepoSpecType): RepoSpecType is the type of the repository
        http_config (HttpConfig):
    """

    url: str
    type: RepoSpecType
    http_config: "HttpConfig"

    def to_dict(self) -> Dict[str, Any]:
        url = self.url

        type: str = self.type

        http_config = self.http_config.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "url": url,
                "type": type,
                "httpConfig": http_config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.http_config import HttpConfig

        d = src_dict.copy()
        url = d.pop("url")

        type = check_repo_spec_type(d.pop("type"))

        http_config = HttpConfig.from_dict(d.pop("httpConfig"))

        http_repo_spec = cls(
            url=url,
            type=type,
            http_config=http_config,
        )

        return http_repo_spec

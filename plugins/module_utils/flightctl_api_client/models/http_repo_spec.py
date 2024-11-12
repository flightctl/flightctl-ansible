from typing import TYPE_CHECKING, Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.repo_spec_type import RepoSpecType, check_repo_spec_type
from ..types import UNSET, Unset

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
        validation_suffix (Union[Unset, str]): URL suffix used only for validating access to the repository. Users might
            use the URL field as a root URL to be used by config sources adding suffixes. This will help with the validation
            of the http endpoint.
    """

    url: str
    type: RepoSpecType
    http_config: "HttpConfig"
    validation_suffix: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        url = self.url

        type: str = self.type

        http_config = self.http_config.to_dict()

        validation_suffix = self.validation_suffix

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "url": url,
                "type": type,
                "httpConfig": http_config,
            }
        )
        if validation_suffix is not UNSET:
            field_dict["validationSuffix"] = validation_suffix

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.http_config import HttpConfig

        d = src_dict.copy()
        url = d.pop("url")

        type = check_repo_spec_type(d.pop("type"))

        http_config = HttpConfig.from_dict(d.pop("httpConfig"))

        validation_suffix = d.pop("validationSuffix", UNSET)

        http_repo_spec = cls(
            url=url,
            type=type,
            http_config=http_config,
            validation_suffix=validation_suffix,
        )

        return http_repo_spec

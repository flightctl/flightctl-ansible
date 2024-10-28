from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpConfigProviderSpecHttpRef")


@_attrs_define
class HttpConfigProviderSpecHttpRef:
    """
    Attributes:
        repository (str): The name of the repository resource to use as the sync source
        file_path (str): The path of the file where the response is stored in the filesystem of the device.
        suffix (Union[Unset, str]): Part of the URL that comes after the base URL. It can include query parameters such
            as:
            /path/to/endpoint?query=param
    """

    repository: str
    file_path: str
    suffix: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        repository = self.repository

        file_path = self.file_path

        suffix = self.suffix

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository": repository,
                "filePath": file_path,
            }
        )
        if suffix is not UNSET:
            field_dict["suffix"] = suffix

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        repository = d.pop("repository")

        file_path = d.pop("filePath")

        suffix = d.pop("suffix", UNSET)

        http_config_provider_spec_http_ref = cls(
            repository=repository,
            file_path=file_path,
            suffix=suffix,
        )

        http_config_provider_spec_http_ref.additional_properties = d
        return http_config_provider_spec_http_ref

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

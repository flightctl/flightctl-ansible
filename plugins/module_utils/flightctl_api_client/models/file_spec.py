from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.file_spec_content_encoding import (
    FileSpecContentEncoding,
    check_file_spec_content_encoding,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="FileSpec")


@_attrs_define
class FileSpec:
    """
    Attributes:
        path (str): The absolute path to the file on the device. Note that any existing file will be overwritten.
        content (str): The plain text (UTF-8) or base64-encoded content of the file.
        content_encoding (Union[Unset, FileSpecContentEncoding]): How the contents are encoded. Must be either "plain"
            or "base64". Defaults to "plain".
        mode (Union[Unset, int]): The file’s permission mode. You may specify the more familiar octal with a leading
            zero (e.g., 0644) or as
            a decimal without a leading zero (e.g., 420). Setuid/setgid/sticky bits are supported. If not specified,
            the permission mode for files defaults to 0644.
        user (Union[Unset, str]): The file's owner, specified either as a name or numeric ID. Defaults to "root".
        group (Union[Unset, str]): The file's group, specified either as a name or numeric ID. Defaults to "root".
    """

    path: str
    content: str
    content_encoding: Union[Unset, FileSpecContentEncoding] = UNSET
    mode: Union[Unset, int] = UNSET
    user: Union[Unset, str] = UNSET
    group: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        path = self.path

        content = self.content

        content_encoding: Union[Unset, str] = UNSET
        if not isinstance(self.content_encoding, Unset):
            content_encoding = self.content_encoding

        mode = self.mode

        user = self.user

        group = self.group

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "content": content,
            }
        )
        if content_encoding is not UNSET:
            field_dict["contentEncoding"] = content_encoding
        if mode is not UNSET:
            field_dict["mode"] = mode
        if user is not UNSET:
            field_dict["user"] = user
        if group is not UNSET:
            field_dict["group"] = group

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        content = d.pop("content")

        _content_encoding = d.pop("contentEncoding", UNSET)
        content_encoding: Union[Unset, FileSpecContentEncoding]
        if isinstance(_content_encoding, Unset):
            content_encoding = UNSET
        else:
            content_encoding = check_file_spec_content_encoding(_content_encoding)

        mode = d.pop("mode", UNSET)

        user = d.pop("user", UNSET)

        group = d.pop("group", UNSET)

        file_spec = cls(
            path=path,
            content=content,
            content_encoding=content_encoding,
            mode=mode,
            user=user,
            group=group,
        )

        file_spec.additional_properties = d
        return file_spec

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

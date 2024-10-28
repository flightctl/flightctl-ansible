from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListMeta")


@_attrs_define
class ListMeta:
    """ListMeta describes metadata that synthetic resources must have, including lists and various status objects. A
    resource may have only one of {ObjectMeta, ListMeta}.

        Attributes:
            continue_ (Union[Unset, str]): continue may be set if the user set a limit on the number of items returned, and
                indicates that the server has more data available. The value is opaque and may be used to issue another request
                to the endpoint that served this list to retrieve the next set of available objects. Continuing a consistent
                list may not be possible if the server configuration has changed or more than a few minutes have passed. The
                resourceVersion field returned when using this continue value will be identical to the value in the first
                response, unless you have received this token from an error message.
            remaining_item_count (Union[Unset, int]): remainingItemCount is the number of subsequent items in the list which
                are not included in this list response. If the list request contained label or field selectors, then the number
                of remaining items is unknown and the field will be left unset and omitted during serialization. If the list is
                complete (either because it is not chunking or because this is the last chunk), then there are no more remaining
                items and this field will be left unset and omitted during serialization. Servers older than v1.15 do not set
                this field. The intended use of the remainingItemCount is *estimating* the size of a collection. Clients should
                not rely on the remainingItemCount to be set or to be exact.
    """

    continue_: Union[Unset, str] = UNSET
    remaining_item_count: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        continue_ = self.continue_

        remaining_item_count = self.remaining_item_count

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if continue_ is not UNSET:
            field_dict["continue"] = continue_
        if remaining_item_count is not UNSET:
            field_dict["remainingItemCount"] = remaining_item_count

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        continue_ = d.pop("continue", UNSET)

        remaining_item_count = d.pop("remainingItemCount", UNSET)

        list_meta = cls(
            continue_=continue_,
            remaining_item_count=remaining_item_count,
        )

        list_meta.additional_properties = d
        return list_meta

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

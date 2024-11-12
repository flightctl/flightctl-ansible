from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.label_selector import LabelSelector


T = TypeVar("T", bound="Batch")


@_attrs_define
class Batch:
    """Batch is an element in batch sequence.

    Attributes:
        selector (Union[Unset, LabelSelector]): A map of key,value pairs that are ANDed. Empty/null label selectors
            match nothing.
        success_threshold (Union[Unset, str]): Percentage is the string format representing percentage string.
        limit (Union[Unset, int, str]):
    """

    selector: Union[Unset, "LabelSelector"] = UNSET
    success_threshold: Union[Unset, str] = UNSET
    limit: Union[Unset, int, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        selector: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.selector, Unset):
            selector = self.selector.to_dict()

        success_threshold = self.success_threshold

        limit: Union[Unset, int, str]
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if selector is not UNSET:
            field_dict["selector"] = selector
        if success_threshold is not UNSET:
            field_dict["successThreshold"] = success_threshold
        if limit is not UNSET:
            field_dict["limit"] = limit

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.label_selector import LabelSelector

        d = src_dict.copy()
        _selector = d.pop("selector", UNSET)
        selector: Union[Unset, LabelSelector]
        if isinstance(_selector, Unset):
            selector = UNSET
        else:
            selector = LabelSelector.from_dict(_selector)

        success_threshold = d.pop("successThreshold", UNSET)

        def _parse_limit(data: object) -> Union[Unset, int, str]:
            if isinstance(data, Unset):
                return data
            return cast(Union[Unset, int, str], data)

        limit = _parse_limit(d.pop("limit", UNSET))

        batch = cls(
            selector=selector,
            success_threshold=success_threshold,
            limit=limit,
        )

        batch.additional_properties = d
        return batch

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

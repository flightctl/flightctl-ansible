from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.label_selector_match_labels import LabelSelectorMatchLabels


T = TypeVar("T", bound="LabelSelector")


@_attrs_define
class LabelSelector:
    """A map of key,value pairs that are ANDed. Empty/null label selectors match nothing.

    Attributes:
        match_labels (LabelSelectorMatchLabels):
    """

    match_labels: "LabelSelectorMatchLabels"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        match_labels = self.match_labels.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "matchLabels": match_labels,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.label_selector_match_labels import LabelSelectorMatchLabels

        d = src_dict.copy()
        match_labels = LabelSelectorMatchLabels.from_dict(d.pop("matchLabels"))

        label_selector = cls(
            match_labels=match_labels,
        )

        label_selector.additional_properties = d
        return label_selector

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

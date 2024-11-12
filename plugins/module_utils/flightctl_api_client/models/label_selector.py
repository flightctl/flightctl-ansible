from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.label_selector_match_labels import LabelSelectorMatchLabels
    from ..models.match_expression import MatchExpression


T = TypeVar("T", bound="LabelSelector")


@_attrs_define
class LabelSelector:
    """A map of key,value pairs that are ANDed. Empty/null label selectors match nothing.

    Attributes:
        match_labels (Union[Unset, LabelSelectorMatchLabels]):
        match_expressions (Union[Unset, List['MatchExpression']]):
    """

    match_labels: Union[Unset, "LabelSelectorMatchLabels"] = UNSET
    match_expressions: Union[Unset, List["MatchExpression"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        match_labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.match_labels, Unset):
            match_labels = self.match_labels.to_dict()

        match_expressions: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.match_expressions, Unset):
            match_expressions = []
            for componentsschemas_match_expressions_item_data in self.match_expressions:
                componentsschemas_match_expressions_item = (
                    componentsschemas_match_expressions_item_data.to_dict()
                )
                match_expressions.append(componentsschemas_match_expressions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match_labels is not UNSET:
            field_dict["matchLabels"] = match_labels
        if match_expressions is not UNSET:
            field_dict["matchExpressions"] = match_expressions

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.label_selector_match_labels import LabelSelectorMatchLabels
        from ..models.match_expression import MatchExpression

        d = src_dict.copy()
        _match_labels = d.pop("matchLabels", UNSET)
        match_labels: Union[Unset, LabelSelectorMatchLabels]
        if isinstance(_match_labels, Unset):
            match_labels = UNSET
        else:
            match_labels = LabelSelectorMatchLabels.from_dict(_match_labels)

        match_expressions = []
        _match_expressions = d.pop("matchExpressions", UNSET)
        for componentsschemas_match_expressions_item_data in _match_expressions or []:
            componentsschemas_match_expressions_item = MatchExpression.from_dict(
                componentsschemas_match_expressions_item_data
            )

            match_expressions.append(componentsschemas_match_expressions_item)

        label_selector = cls(
            match_labels=match_labels,
            match_expressions=match_expressions,
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

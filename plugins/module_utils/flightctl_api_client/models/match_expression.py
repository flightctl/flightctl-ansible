from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.match_expression_operator import (
    MatchExpressionOperator,
    check_match_expression_operator,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="MatchExpression")


@_attrs_define
class MatchExpression:
    """
    Attributes:
        key (str):
        operator (MatchExpressionOperator):
        values (Union[Unset, List[str]]):
    """

    key: str
    operator: MatchExpressionOperator
    values: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        key = self.key

        operator: str = self.operator

        values: Union[Unset, List[str]] = UNSET
        if not isinstance(self.values, Unset):
            values = self.values

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
                "operator": operator,
            }
        )
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        key = d.pop("key")

        operator = check_match_expression_operator(d.pop("operator"))

        values = cast(List[str], d.pop("values", UNSET))

        match_expression = cls(
            key=key,
            operator=operator,
            values=values,
        )

        match_expression.additional_properties = d
        return match_expression

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

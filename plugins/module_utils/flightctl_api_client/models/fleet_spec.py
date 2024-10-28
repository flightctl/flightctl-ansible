from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.fleet_spec_template import FleetSpecTemplate
    from ..models.label_selector import LabelSelector


T = TypeVar("T", bound="FleetSpec")


@_attrs_define
class FleetSpec:
    """FleetSpec is a description of a fleet's target state.

    Attributes:
        template (FleetSpecTemplate):
        selector (Union[Unset, LabelSelector]): A map of key,value pairs that are ANDed. Empty/null label selectors
            match nothing.
    """

    template: "FleetSpecTemplate"
    selector: Union[Unset, "LabelSelector"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        template = self.template.to_dict()

        selector: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.selector, Unset):
            selector = self.selector.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template": template,
            }
        )
        if selector is not UNSET:
            field_dict["selector"] = selector

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.fleet_spec_template import FleetSpecTemplate
        from ..models.label_selector import LabelSelector

        d = src_dict.copy()
        template = FleetSpecTemplate.from_dict(d.pop("template"))

        _selector = d.pop("selector", UNSET)
        selector: Union[Unset, LabelSelector]
        if isinstance(_selector, Unset):
            selector = UNSET
        else:
            selector = LabelSelector.from_dict(_selector)

        fleet_spec = cls(
            template=template,
            selector=selector,
        )

        fleet_spec.additional_properties = d
        return fleet_spec

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

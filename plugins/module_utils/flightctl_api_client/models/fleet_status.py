from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.condition import Condition
    from ..models.devices_summary import DevicesSummary


T = TypeVar("T", bound="FleetStatus")


@_attrs_define
class FleetStatus:
    """FleetStatus represents information about the status of a fleet. Status may trail the actual state of a fleet,
    especially if devices of a fleet have not contacted the management service in a while.

        Attributes:
            conditions (List['Condition']): Current state of the fleet.
            devices_summary (Union[Unset, DevicesSummary]): A summary of the devices in the fleet returned when fetching a
                single Fleet.
    """

    conditions: List["Condition"]
    devices_summary: Union[Unset, "DevicesSummary"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        conditions = []
        for conditions_item_data in self.conditions:
            conditions_item = conditions_item_data.to_dict()
            conditions.append(conditions_item)

        devices_summary: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.devices_summary, Unset):
            devices_summary = self.devices_summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "conditions": conditions,
            }
        )
        if devices_summary is not UNSET:
            field_dict["devicesSummary"] = devices_summary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.condition import Condition
        from ..models.devices_summary import DevicesSummary

        d = src_dict.copy()
        conditions = []
        _conditions = d.pop("conditions")
        for conditions_item_data in _conditions:
            conditions_item = Condition.from_dict(conditions_item_data)

            conditions.append(conditions_item)

        _devices_summary = d.pop("devicesSummary", UNSET)
        devices_summary: Union[Unset, DevicesSummary]
        if isinstance(_devices_summary, Unset):
            devices_summary = UNSET
        else:
            devices_summary = DevicesSummary.from_dict(_devices_summary)

        fleet_status = cls(
            conditions=conditions,
            devices_summary=devices_summary,
        )

        fleet_status.additional_properties = d
        return fleet_status

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

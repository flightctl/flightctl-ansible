from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.resource_alert_rule import ResourceAlertRule


T = TypeVar("T", bound="ResourceMonitorSpec")


@_attrs_define
class ResourceMonitorSpec:
    """
    Attributes:
        monitor_type (str):
        alert_rules (List['ResourceAlertRule']): Array of alert rules. Only one alert per severity is allowed.
        sampling_interval (str): Duration between monitor samples. Format: positive integer followed by 's' for seconds,
            'm' for minutes, 'h' for hours.
    """

    monitor_type: str
    alert_rules: List["ResourceAlertRule"]
    sampling_interval: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        monitor_type = self.monitor_type

        alert_rules = []
        for alert_rules_item_data in self.alert_rules:
            alert_rules_item = alert_rules_item_data.to_dict()
            alert_rules.append(alert_rules_item)

        sampling_interval = self.sampling_interval

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "monitorType": monitor_type,
                "alertRules": alert_rules,
                "samplingInterval": sampling_interval,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.resource_alert_rule import ResourceAlertRule

        d = src_dict.copy()
        monitor_type = d.pop("monitorType")

        alert_rules = []
        _alert_rules = d.pop("alertRules")
        for alert_rules_item_data in _alert_rules:
            alert_rules_item = ResourceAlertRule.from_dict(alert_rules_item_data)

            alert_rules.append(alert_rules_item)

        sampling_interval = d.pop("samplingInterval")

        resource_monitor_spec = cls(
            monitor_type=monitor_type,
            alert_rules=alert_rules,
            sampling_interval=sampling_interval,
        )

        resource_monitor_spec.additional_properties = d
        return resource_monitor_spec

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

from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.resource_alert_severity_type import (
    ResourceAlertSeverityType,
    check_resource_alert_severity_type,
)

T = TypeVar("T", bound="ResourceAlertRule")


@_attrs_define
class ResourceAlertRule:
    """
    Attributes:
        severity (ResourceAlertSeverityType):
        duration (str): Duration is the time over which the average usage is observed before alerting. Format: positive
            integer followed by 's' for seconds, 'm' for minutes, 'h' for hours.
        percentage (float): The percentage of usage that triggers the alert.
        description (str): A human-readable description of the alert.
    """

    severity: ResourceAlertSeverityType
    duration: str
    percentage: float
    description: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        severity: str = self.severity

        duration = self.duration

        percentage = self.percentage

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "severity": severity,
                "duration": duration,
                "percentage": percentage,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        severity = check_resource_alert_severity_type(d.pop("severity"))

        duration = d.pop("duration")

        percentage = d.pop("percentage")

        description = d.pop("description")

        resource_alert_rule = cls(
            severity=severity,
            duration=duration,
            percentage=percentage,
            description=description,
        )

        resource_alert_rule.additional_properties = d
        return resource_alert_rule

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

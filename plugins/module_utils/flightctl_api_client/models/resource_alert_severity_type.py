from typing import Literal, Set, cast

ResourceAlertSeverityType = Literal["Critical", "Info", "Warning"]

RESOURCE_ALERT_SEVERITY_TYPE_VALUES: Set[ResourceAlertSeverityType] = {
    "Critical",
    "Info",
    "Warning",
}


def check_resource_alert_severity_type(value: str) -> ResourceAlertSeverityType:
    if value in RESOURCE_ALERT_SEVERITY_TYPE_VALUES:
        return cast(ResourceAlertSeverityType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {RESOURCE_ALERT_SEVERITY_TYPE_VALUES!r}"
    )

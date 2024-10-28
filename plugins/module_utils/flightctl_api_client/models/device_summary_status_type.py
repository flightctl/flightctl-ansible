from typing import Literal, Set, cast

DeviceSummaryStatusType = Literal[
    "Degraded", "Error", "Online", "PoweredOff", "Rebooting", "Unknown"
]

DEVICE_SUMMARY_STATUS_TYPE_VALUES: Set[DeviceSummaryStatusType] = {
    "Degraded",
    "Error",
    "Online",
    "PoweredOff",
    "Rebooting",
    "Unknown",
}


def check_device_summary_status_type(value: str) -> DeviceSummaryStatusType:
    if value in DEVICE_SUMMARY_STATUS_TYPE_VALUES:
        return cast(DeviceSummaryStatusType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {DEVICE_SUMMARY_STATUS_TYPE_VALUES!r}"
    )

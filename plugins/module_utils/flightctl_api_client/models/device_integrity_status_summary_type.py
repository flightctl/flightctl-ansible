from typing import Literal, Set, cast

DeviceIntegrityStatusSummaryType = Literal["Failed", "Passed", "Unknown", "Unsupported"]

DEVICE_INTEGRITY_STATUS_SUMMARY_TYPE_VALUES: Set[DeviceIntegrityStatusSummaryType] = {
    "Failed",
    "Passed",
    "Unknown",
    "Unsupported",
}


def check_device_integrity_status_summary_type(
    value: str,
) -> DeviceIntegrityStatusSummaryType:
    if value in DEVICE_INTEGRITY_STATUS_SUMMARY_TYPE_VALUES:
        return cast(DeviceIntegrityStatusSummaryType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {DEVICE_INTEGRITY_STATUS_SUMMARY_TYPE_VALUES!r}"
    )

from typing import Literal, Set, cast

DeviceResourceStatusType = Literal["Critical", "Error", "Healthy", "Unknown", "Warning"]

DEVICE_RESOURCE_STATUS_TYPE_VALUES: Set[DeviceResourceStatusType] = {
    "Critical",
    "Error",
    "Healthy",
    "Unknown",
    "Warning",
}


def check_device_resource_status_type(value: str) -> DeviceResourceStatusType:
    if value in DEVICE_RESOURCE_STATUS_TYPE_VALUES:
        return cast(DeviceResourceStatusType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {DEVICE_RESOURCE_STATUS_TYPE_VALUES!r}"
    )

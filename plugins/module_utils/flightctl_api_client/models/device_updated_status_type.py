from typing import Literal, Set, cast

DeviceUpdatedStatusType = Literal["OutOfDate", "Unknown", "Updating", "UpToDate"]

DEVICE_UPDATED_STATUS_TYPE_VALUES: Set[DeviceUpdatedStatusType] = {
    "OutOfDate",
    "Unknown",
    "Updating",
    "UpToDate",
}


def check_device_updated_status_type(value: str) -> DeviceUpdatedStatusType:
    if value in DEVICE_UPDATED_STATUS_TYPE_VALUES:
        return cast(DeviceUpdatedStatusType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {DEVICE_UPDATED_STATUS_TYPE_VALUES!r}"
    )

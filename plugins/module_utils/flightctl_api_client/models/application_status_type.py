from typing import Literal, Set, cast

ApplicationStatusType = Literal[
    "Completed", "Error", "Preparing", "Running", "Starting", "Unknown"
]

APPLICATION_STATUS_TYPE_VALUES: Set[ApplicationStatusType] = {
    "Completed",
    "Error",
    "Preparing",
    "Running",
    "Starting",
    "Unknown",
}


def check_application_status_type(value: str) -> ApplicationStatusType:
    if value in APPLICATION_STATUS_TYPE_VALUES:
        return cast(ApplicationStatusType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {APPLICATION_STATUS_TYPE_VALUES!r}"
    )

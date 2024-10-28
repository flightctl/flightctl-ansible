from typing import Literal, Set, cast

ApplicationsSummaryStatusType = Literal["Degraded", "Error", "Healthy", "Unknown"]

APPLICATIONS_SUMMARY_STATUS_TYPE_VALUES: Set[ApplicationsSummaryStatusType] = {
    "Degraded",
    "Error",
    "Healthy",
    "Unknown",
}


def check_applications_summary_status_type(value: str) -> ApplicationsSummaryStatusType:
    if value in APPLICATIONS_SUMMARY_STATUS_TYPE_VALUES:
        return cast(ApplicationsSummaryStatusType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {APPLICATIONS_SUMMARY_STATUS_TYPE_VALUES!r}"
    )

from typing import Literal, Set, cast

ConditionStatus = Literal["False", "True", "Unknown"]

CONDITION_STATUS_VALUES: Set[ConditionStatus] = {
    "False",
    "True",
    "Unknown",
}


def check_condition_status(value: str) -> ConditionStatus:
    if value in CONDITION_STATUS_VALUES:
        return cast(ConditionStatus, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CONDITION_STATUS_VALUES!r}"
    )

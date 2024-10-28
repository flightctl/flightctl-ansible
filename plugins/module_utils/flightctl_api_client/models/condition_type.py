from typing import Literal, Set, cast

ConditionType = Literal[
    "Accessible",
    "Approved",
    "Denied",
    "Failed",
    "MultipleOwners",
    "OverlappingSelectors",
    "ResourceParsed",
    "SpecValid",
    "Synced",
    "Updating",
    "Valid",
]

CONDITION_TYPE_VALUES: Set[ConditionType] = {
    "Accessible",
    "Approved",
    "Denied",
    "Failed",
    "MultipleOwners",
    "OverlappingSelectors",
    "ResourceParsed",
    "SpecValid",
    "Synced",
    "Updating",
    "Valid",
}


def check_condition_type(value: str) -> ConditionType:
    if value in CONDITION_TYPE_VALUES:
        return cast(ConditionType, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {CONDITION_TYPE_VALUES!r}"
    )

from typing import Literal, Set, cast

SortOrder = Literal["Asc", "Desc"]

SORT_ORDER_VALUES: Set[SortOrder] = {
    "Asc",
    "Desc",
}


def check_sort_order(value: str) -> SortOrder:
    if value in SORT_ORDER_VALUES:
        return cast(SortOrder, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {SORT_ORDER_VALUES!r}"
    )

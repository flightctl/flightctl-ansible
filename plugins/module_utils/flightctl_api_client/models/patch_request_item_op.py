from typing import Literal, Set, cast

PatchRequestItemOp = Literal["add", "remove", "replace"]

PATCH_REQUEST_ITEM_OP_VALUES: Set[PatchRequestItemOp] = {
    "add",
    "remove",
    "replace",
}


def check_patch_request_item_op(value: str) -> PatchRequestItemOp:
    if value in PATCH_REQUEST_ITEM_OP_VALUES:
        return cast(PatchRequestItemOp, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {PATCH_REQUEST_ITEM_OP_VALUES!r}"
    )

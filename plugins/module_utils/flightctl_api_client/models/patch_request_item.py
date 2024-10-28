from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..models.patch_request_item_op import (
    PatchRequestItemOp,
    check_patch_request_item_op,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="PatchRequestItem")


@_attrs_define
class PatchRequestItem:
    """
    Attributes:
        path (str): A JSON Pointer path.
        op (PatchRequestItemOp): The operation to perform.
        value (Union[Unset, Any]): The value to add or replace.
    """

    path: str
    op: PatchRequestItemOp
    value: Union[Unset, Any] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        path = self.path

        op: str = self.op

        value = self.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "path": path,
                "op": op,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        path = d.pop("path")

        op = check_patch_request_item_op(d.pop("op"))

        value = d.pop("value", UNSET)

        patch_request_item = cls(
            path=path,
            op=op,
            value=value,
        )

        return patch_request_item

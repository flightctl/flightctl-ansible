from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch import Batch


T = TypeVar("T", bound="BatchSequence")


@_attrs_define
class BatchSequence:
    """BatchSequence defines the list of batches to be executed in sequence.

    Attributes:
        sequence (Union[Unset, List['Batch']]):
    """

    sequence: Union[Unset, List["Batch"]] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sequence: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.sequence, Unset):
            sequence = []
            for sequence_item_data in self.sequence:
                sequence_item = sequence_item_data.to_dict()
                sequence.append(sequence_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sequence is not UNSET:
            field_dict["sequence"] = sequence

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch import Batch

        d = src_dict.copy()
        sequence = []
        _sequence = d.pop("sequence", UNSET)
        for sequence_item_data in _sequence or []:
            sequence_item = Batch.from_dict(sequence_item_data)

            sequence.append(sequence_item)

        batch_sequence = cls(
            sequence=sequence,
        )

        batch_sequence.additional_properties = d
        return batch_sequence

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

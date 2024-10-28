from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_spec import DeviceSpec
    from ..models.object_meta import ObjectMeta


T = TypeVar("T", bound="FleetSpecTemplate")


@_attrs_define
class FleetSpecTemplate:
    """
    Attributes:
        spec (DeviceSpec):
        metadata (Union[Unset, ObjectMeta]): ObjectMeta is metadata that all persisted resources must have, which
            includes all objects users must create.
    """

    spec: "DeviceSpec"
    metadata: Union[Unset, "ObjectMeta"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        spec = self.spec.to_dict()

        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "spec": spec,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device_spec import DeviceSpec
        from ..models.object_meta import ObjectMeta

        d = src_dict.copy()
        spec = DeviceSpec.from_dict(d.pop("spec"))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ObjectMeta]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ObjectMeta.from_dict(_metadata)

        fleet_spec_template = cls(
            spec=spec,
            metadata=metadata,
        )

        fleet_spec_template.additional_properties = d
        return fleet_spec_template

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

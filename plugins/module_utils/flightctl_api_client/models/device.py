from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_spec import DeviceSpec
    from ..models.device_status import DeviceStatus
    from ..models.object_meta import ObjectMeta


T = TypeVar("T", bound="Device")


@_attrs_define
class Device:
    """Device represents a physical device.

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ObjectMeta): ObjectMeta is metadata that all persisted resources must have, which includes all objects
            users must create.
        spec (Union[Unset, DeviceSpec]):
        status (Union[Unset, DeviceStatus]): DeviceStatus represents information about the status of a device. Status
            may trail the actual state of a device.
    """

    api_version: str
    kind: str
    metadata: "ObjectMeta"
    spec: Union[Unset, "DeviceSpec"] = UNSET
    status: Union[Unset, "DeviceStatus"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

        spec: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.spec, Unset):
            spec = self.spec.to_dict()

        status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apiVersion": api_version,
                "kind": kind,
                "metadata": metadata,
            }
        )
        if spec is not UNSET:
            field_dict["spec"] = spec
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device_spec import DeviceSpec
        from ..models.device_status import DeviceStatus
        from ..models.object_meta import ObjectMeta

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ObjectMeta.from_dict(d.pop("metadata"))

        _spec = d.pop("spec", UNSET)
        spec: Union[Unset, DeviceSpec]
        if isinstance(_spec, Unset):
            spec = UNSET
        else:
            spec = DeviceSpec.from_dict(_spec)

        _status = d.pop("status", UNSET)
        status: Union[Unset, DeviceStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DeviceStatus.from_dict(_status)

        device = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            spec=spec,
            status=status,
        )

        device.additional_properties = d
        return device

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

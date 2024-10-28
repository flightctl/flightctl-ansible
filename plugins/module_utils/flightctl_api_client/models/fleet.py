from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.fleet_spec import FleetSpec
    from ..models.fleet_status import FleetStatus
    from ..models.object_meta import ObjectMeta


T = TypeVar("T", bound="Fleet")


@_attrs_define
class Fleet:
    """Fleet represents a set of devices.

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ObjectMeta): ObjectMeta is metadata that all persisted resources must have, which includes all objects
            users must create.
        spec (FleetSpec): FleetSpec is a description of a fleet's target state.
        status (Union[Unset, FleetStatus]): FleetStatus represents information about the status of a fleet. Status may
            trail the actual state of a fleet, especially if devices of a fleet have not contacted the management service in
            a while.
    """

    api_version: str
    kind: str
    metadata: "ObjectMeta"
    spec: "FleetSpec"
    status: Union[Unset, "FleetStatus"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

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
                "spec": spec,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.fleet_spec import FleetSpec
        from ..models.fleet_status import FleetStatus
        from ..models.object_meta import ObjectMeta

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ObjectMeta.from_dict(d.pop("metadata"))

        spec = FleetSpec.from_dict(d.pop("spec"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, FleetStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = FleetStatus.from_dict(_status)

        fleet = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            spec=spec,
            status=status,
        )

        fleet.additional_properties = d
        return fleet

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

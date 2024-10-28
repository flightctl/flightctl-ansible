from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device import Device
    from ..models.devices_summary import DevicesSummary
    from ..models.list_meta import ListMeta


T = TypeVar("T", bound="DeviceList")


@_attrs_define
class DeviceList:
    """DeviceList is a list of Devices.

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ListMeta): ListMeta describes metadata that synthetic resources must have, including lists and various
            status objects. A resource may have only one of {ObjectMeta, ListMeta}.
        items (List['Device']): List of Devices.
        summary (Union[Unset, DevicesSummary]): A summary of the devices in the fleet returned when fetching a single
            Fleet.
    """

    api_version: str
    kind: str
    metadata: "ListMeta"
    items: List["Device"]
    summary: Union[Unset, "DevicesSummary"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

        summary: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.summary, Unset):
            summary = self.summary.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apiVersion": api_version,
                "kind": kind,
                "metadata": metadata,
                "items": items,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device import Device
        from ..models.devices_summary import DevicesSummary
        from ..models.list_meta import ListMeta

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ListMeta.from_dict(d.pop("metadata"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = Device.from_dict(items_item_data)

            items.append(items_item)

        _summary = d.pop("summary", UNSET)
        summary: Union[Unset, DevicesSummary]
        if isinstance(_summary, Unset):
            summary = UNSET
        else:
            summary = DevicesSummary.from_dict(_summary)

        device_list = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            items=items,
            summary=summary,
        )

        device_list.additional_properties = d
        return device_list

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

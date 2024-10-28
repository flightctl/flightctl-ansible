from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.fleet import Fleet
    from ..models.list_meta import ListMeta


T = TypeVar("T", bound="FleetList")


@_attrs_define
class FleetList:
    """FleetList is a list of Fleets.

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ListMeta): ListMeta describes metadata that synthetic resources must have, including lists and various
            status objects. A resource may have only one of {ObjectMeta, ListMeta}.
        items (List['Fleet']): List of Fleets.
    """

    api_version: str
    kind: str
    metadata: "ListMeta"
    items: List["Fleet"]
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

        items = []
        for items_item_data in self.items:
            items_item = items_item_data.to_dict()
            items.append(items_item)

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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.fleet import Fleet
        from ..models.list_meta import ListMeta

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ListMeta.from_dict(d.pop("metadata"))

        items = []
        _items = d.pop("items")
        for items_item_data in _items:
            items_item = Fleet.from_dict(items_item_data)

            items.append(items_item)

        fleet_list = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            items=items,
        )

        fleet_list.additional_properties = d
        return fleet_list

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

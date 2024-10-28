import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.object_meta_annotations import ObjectMetaAnnotations
    from ..models.object_meta_labels import ObjectMetaLabels


T = TypeVar("T", bound="ObjectMeta")


@_attrs_define
class ObjectMeta:
    """ObjectMeta is metadata that all persisted resources must have, which includes all objects users must create.

    Attributes:
        creation_timestamp (Union[Unset, datetime.datetime]):
        deletion_timestamp (Union[Unset, datetime.datetime]):
        name (Union[Unset, str]): name of the object
        labels (Union[Unset, ObjectMetaLabels]): Map of string keys and values that can be used to organize and
            categorize (scope and select) objects.
        generation (Union[Unset, int]): A sequence number representing a specific generation of the desired state.
            Populated by the system. Read-only.
        owner (Union[Unset, str]): A resource that owns this resource, in "kind/name" format.
        annotations (Union[Unset, ObjectMetaAnnotations]): Properties set by the service.
        resource_version (Union[Unset, str]): An opaque string that identifies the server's internal version of an
            object.
    """

    creation_timestamp: Union[Unset, datetime.datetime] = UNSET
    deletion_timestamp: Union[Unset, datetime.datetime] = UNSET
    name: Union[Unset, str] = UNSET
    labels: Union[Unset, "ObjectMetaLabels"] = UNSET
    generation: Union[Unset, int] = UNSET
    owner: Union[Unset, str] = UNSET
    annotations: Union[Unset, "ObjectMetaAnnotations"] = UNSET
    resource_version: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        creation_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.creation_timestamp, Unset):
            creation_timestamp = self.creation_timestamp.isoformat()

        deletion_timestamp: Union[Unset, str] = UNSET
        if not isinstance(self.deletion_timestamp, Unset):
            deletion_timestamp = self.deletion_timestamp.isoformat()

        name = self.name

        labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        generation = self.generation

        owner = self.owner

        annotations: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.annotations, Unset):
            annotations = self.annotations.to_dict()

        resource_version = self.resource_version

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if creation_timestamp is not UNSET:
            field_dict["creationTimestamp"] = creation_timestamp
        if deletion_timestamp is not UNSET:
            field_dict["deletionTimestamp"] = deletion_timestamp
        if name is not UNSET:
            field_dict["name"] = name
        if labels is not UNSET:
            field_dict["labels"] = labels
        if generation is not UNSET:
            field_dict["generation"] = generation
        if owner is not UNSET:
            field_dict["owner"] = owner
        if annotations is not UNSET:
            field_dict["annotations"] = annotations
        if resource_version is not UNSET:
            field_dict["resourceVersion"] = resource_version

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.object_meta_annotations import ObjectMetaAnnotations
        from ..models.object_meta_labels import ObjectMetaLabels

        d = src_dict.copy()
        _creation_timestamp = d.pop("creationTimestamp", UNSET)
        creation_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_creation_timestamp, Unset):
            creation_timestamp = UNSET
        else:
            creation_timestamp = isoparse(_creation_timestamp)

        _deletion_timestamp = d.pop("deletionTimestamp", UNSET)
        deletion_timestamp: Union[Unset, datetime.datetime]
        if isinstance(_deletion_timestamp, Unset):
            deletion_timestamp = UNSET
        else:
            deletion_timestamp = isoparse(_deletion_timestamp)

        name = d.pop("name", UNSET)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, ObjectMetaLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = ObjectMetaLabels.from_dict(_labels)

        generation = d.pop("generation", UNSET)

        owner = d.pop("owner", UNSET)

        _annotations = d.pop("annotations", UNSET)
        annotations: Union[Unset, ObjectMetaAnnotations]
        if isinstance(_annotations, Unset):
            annotations = UNSET
        else:
            annotations = ObjectMetaAnnotations.from_dict(_annotations)

        resource_version = d.pop("resourceVersion", UNSET)

        object_meta = cls(
            creation_timestamp=creation_timestamp,
            deletion_timestamp=deletion_timestamp,
            name=name,
            labels=labels,
            generation=generation,
            owner=owner,
            annotations=annotations,
            resource_version=resource_version,
        )

        object_meta.additional_properties = d
        return object_meta

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

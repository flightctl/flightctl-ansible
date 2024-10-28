from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.generic_repo_spec import GenericRepoSpec
    from ..models.http_repo_spec import HttpRepoSpec
    from ..models.object_meta import ObjectMeta
    from ..models.repository_status import RepositoryStatus
    from ..models.ssh_repo_spec import SshRepoSpec


T = TypeVar("T", bound="Repository")


@_attrs_define
class Repository:
    """Repository represents a Git repository or an HTTP endpoint

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ObjectMeta): ObjectMeta is metadata that all persisted resources must have, which includes all objects
            users must create.
        spec (Union['GenericRepoSpec', 'HttpRepoSpec', 'SshRepoSpec']):
        status (Union[Unset, RepositoryStatus]): RepositoryStatus represents information about the status of a
            repository. Status may trail the actual state of a repository.
    """

    api_version: str
    kind: str
    metadata: "ObjectMeta"
    spec: Union["GenericRepoSpec", "HttpRepoSpec", "SshRepoSpec"]
    status: Union[Unset, "RepositoryStatus"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.generic_repo_spec import GenericRepoSpec
        from ..models.http_repo_spec import HttpRepoSpec

        api_version = self.api_version

        kind = self.kind

        metadata = self.metadata.to_dict()

        spec: Dict[str, Any]
        if isinstance(self.spec, GenericRepoSpec):
            spec = self.spec.to_dict()
        elif isinstance(self.spec, HttpRepoSpec):
            spec = self.spec.to_dict()
        else:
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
        from ..models.generic_repo_spec import GenericRepoSpec
        from ..models.http_repo_spec import HttpRepoSpec
        from ..models.object_meta import ObjectMeta
        from ..models.repository_status import RepositoryStatus
        from ..models.ssh_repo_spec import SshRepoSpec

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ObjectMeta.from_dict(d.pop("metadata"))

        def _parse_spec(
            data: object,
        ) -> Union["GenericRepoSpec", "HttpRepoSpec", "SshRepoSpec"]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_repository_spec_type_0 = GenericRepoSpec.from_dict(
                    data
                )

                return componentsschemas_repository_spec_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_repository_spec_type_1 = HttpRepoSpec.from_dict(data)

                return componentsschemas_repository_spec_type_1
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            componentsschemas_repository_spec_type_2 = SshRepoSpec.from_dict(data)

            return componentsschemas_repository_spec_type_2

        spec = _parse_spec(d.pop("spec"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, RepositoryStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = RepositoryStatus.from_dict(_status)

        repository = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            spec=spec,
            status=status,
        )

        repository.additional_properties = d
        return repository

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

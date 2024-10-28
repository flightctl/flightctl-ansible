from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.certificate_signing_request_spec import CertificateSigningRequestSpec
    from ..models.certificate_signing_request_status import (
        CertificateSigningRequestStatus,
    )
    from ..models.object_meta import ObjectMeta


T = TypeVar("T", bound="CertificateSigningRequest")


@_attrs_define
class CertificateSigningRequest:
    """CertificateSigningRequest represents a request for a signed certificate from the CA

    Attributes:
        api_version (str): APIVersion defines the versioned schema of this representation of an object. Servers should
            convert recognized schemas to the latest internal value, and may reject unrecognized values. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources
        kind (str): Kind is a string value representing the REST resource this object represents. Servers may infer this
            from the endpoint the client submits requests to. Cannot be updated. In CamelCase. More info:
            https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds
        metadata (ObjectMeta): ObjectMeta is metadata that all persisted resources must have, which includes all objects
            users must create.
        spec (CertificateSigningRequestSpec): Wrapper around a user-created CSR, modeled on kubernetes
            io.k8s.api.certificates.v1.CertificateSigningRequestSpec
        status (Union[Unset, CertificateSigningRequestStatus]): Indicates approval/denial/failure status of the CSR, and
            contains the issued certifiate if any exists
    """

    api_version: str
    kind: str
    metadata: "ObjectMeta"
    spec: "CertificateSigningRequestSpec"
    status: Union[Unset, "CertificateSigningRequestStatus"] = UNSET
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
        from ..models.certificate_signing_request_spec import (
            CertificateSigningRequestSpec,
        )
        from ..models.certificate_signing_request_status import (
            CertificateSigningRequestStatus,
        )
        from ..models.object_meta import ObjectMeta

        d = src_dict.copy()
        api_version = d.pop("apiVersion")

        kind = d.pop("kind")

        metadata = ObjectMeta.from_dict(d.pop("metadata"))

        spec = CertificateSigningRequestSpec.from_dict(d.pop("spec"))

        _status = d.pop("status", UNSET)
        status: Union[Unset, CertificateSigningRequestStatus]
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = CertificateSigningRequestStatus.from_dict(_status)

        certificate_signing_request = cls(
            api_version=api_version,
            kind=kind,
            metadata=metadata,
            spec=spec,
            status=status,
        )

        certificate_signing_request.additional_properties = d
        return certificate_signing_request

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

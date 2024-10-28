from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.certificate_signing_request_spec_extra import (
        CertificateSigningRequestSpecExtra,
    )


T = TypeVar("T", bound="CertificateSigningRequestSpec")


@_attrs_define
class CertificateSigningRequestSpec:
    """Wrapper around a user-created CSR, modeled on kubernetes io.k8s.api.certificates.v1.CertificateSigningRequestSpec

    Attributes:
        request (str): The base64-encoded PEM-encoded PKCS#10 CSR. Matches the spec.request field in a kubernetes
            CertificateSigningRequest resource
        signer_name (str): Indicates the requested signer, and is a qualified name
        expiration_seconds (Union[Unset, int]): Requested duration of validity for the certificate
        extra (Union[Unset, CertificateSigningRequestSpecExtra]): Extra attributes of the user that created the CSR,
            populated by the API server on creation and immutable
        uid (Union[Unset, str]): UID of the user that created the CSR, populated by the API server on creation and
            immutable
        usages (Union[Unset, List[str]]): Usages specifies a set of key usages requested in the issued certificate.
        username (Union[Unset, str]): Name of the user that created the CSR, populated by the API server on creation and
            immutable
    """

    request: str
    signer_name: str
    expiration_seconds: Union[Unset, int] = UNSET
    extra: Union[Unset, "CertificateSigningRequestSpecExtra"] = UNSET
    uid: Union[Unset, str] = UNSET
    usages: Union[Unset, List[str]] = UNSET
    username: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        request = self.request

        signer_name = self.signer_name

        expiration_seconds = self.expiration_seconds

        extra: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.extra, Unset):
            extra = self.extra.to_dict()

        uid = self.uid

        usages: Union[Unset, List[str]] = UNSET
        if not isinstance(self.usages, Unset):
            usages = self.usages

        username = self.username

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "request": request,
                "signerName": signer_name,
            }
        )
        if expiration_seconds is not UNSET:
            field_dict["expirationSeconds"] = expiration_seconds
        if extra is not UNSET:
            field_dict["extra"] = extra
        if uid is not UNSET:
            field_dict["uid"] = uid
        if usages is not UNSET:
            field_dict["usages"] = usages
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.certificate_signing_request_spec_extra import (
            CertificateSigningRequestSpecExtra,
        )

        d = src_dict.copy()
        request = d.pop("request")

        signer_name = d.pop("signerName")

        expiration_seconds = d.pop("expirationSeconds", UNSET)

        _extra = d.pop("extra", UNSET)
        extra: Union[Unset, CertificateSigningRequestSpecExtra]
        if isinstance(_extra, Unset):
            extra = UNSET
        else:
            extra = CertificateSigningRequestSpecExtra.from_dict(_extra)

        uid = d.pop("uid", UNSET)

        usages = cast(List[str], d.pop("usages", UNSET))

        username = d.pop("username", UNSET)

        certificate_signing_request_spec = cls(
            request=request,
            signer_name=signer_name,
            expiration_seconds=expiration_seconds,
            extra=extra,
            uid=uid,
            usages=usages,
            username=username,
        )

        certificate_signing_request_spec.additional_properties = d
        return certificate_signing_request_spec

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

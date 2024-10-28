from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="HttpConfig")


@_attrs_define
class HttpConfig:
    """
    Attributes:
        username (Union[Unset, str]): The username for auth with HTTP transport
        password (Union[Unset, str]): The password for auth with HTTP transport
        tls_crt (Union[Unset, str]): Base64 encoded TLS cert data
        tls_key (Union[Unset, str]): Base64 encoded TLS cert key
        ca_crt (Union[Unset, str]): Base64 encoded root CA
        skip_server_verification (Union[Unset, bool]): Skip remote server verification
        token (Union[Unset, str]): The token for auth with HTTP transport
    """

    username: Union[Unset, str] = UNSET
    password: Union[Unset, str] = UNSET
    tls_crt: Union[Unset, str] = UNSET
    tls_key: Union[Unset, str] = UNSET
    ca_crt: Union[Unset, str] = UNSET
    skip_server_verification: Union[Unset, bool] = UNSET
    token: Union[Unset, str] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        password = self.password

        tls_crt = self.tls_crt

        tls_key = self.tls_key

        ca_crt = self.ca_crt

        skip_server_verification = self.skip_server_verification

        token = self.token

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if username is not UNSET:
            field_dict["username"] = username
        if password is not UNSET:
            field_dict["password"] = password
        if tls_crt is not UNSET:
            field_dict["tls.crt"] = tls_crt
        if tls_key is not UNSET:
            field_dict["tls.key"] = tls_key
        if ca_crt is not UNSET:
            field_dict["ca.crt"] = ca_crt
        if skip_server_verification is not UNSET:
            field_dict["skipServerVerification"] = skip_server_verification
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username", UNSET)

        password = d.pop("password", UNSET)

        tls_crt = d.pop("tls.crt", UNSET)

        tls_key = d.pop("tls.key", UNSET)

        ca_crt = d.pop("ca.crt", UNSET)

        skip_server_verification = d.pop("skipServerVerification", UNSET)

        token = d.pop("token", UNSET)

        http_config = cls(
            username=username,
            password=password,
            tls_crt=tls_crt,
            tls_key=tls_key,
            ca_crt=ca_crt,
            skip_server_verification=skip_server_verification,
            token=token,
        )

        return http_config

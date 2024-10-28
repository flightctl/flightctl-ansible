from typing import Any, Dict, Type, TypeVar, Union

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="SshConfig")


@_attrs_define
class SshConfig:
    """
    Attributes:
        ssh_private_key (Union[Unset, str]): Base64 encoded private SSH key
        private_key_passphrase (Union[Unset, str]): The passphrase for sshPrivateKey
        skip_server_verification (Union[Unset, bool]): Skip remote server verification
    """

    ssh_private_key: Union[Unset, str] = UNSET
    private_key_passphrase: Union[Unset, str] = UNSET
    skip_server_verification: Union[Unset, bool] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        ssh_private_key = self.ssh_private_key

        private_key_passphrase = self.private_key_passphrase

        skip_server_verification = self.skip_server_verification

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if ssh_private_key is not UNSET:
            field_dict["sshPrivateKey"] = ssh_private_key
        if private_key_passphrase is not UNSET:
            field_dict["privateKeyPassphrase"] = private_key_passphrase
        if skip_server_verification is not UNSET:
            field_dict["skipServerVerification"] = skip_server_verification

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ssh_private_key = d.pop("sshPrivateKey", UNSET)

        private_key_passphrase = d.pop("privateKeyPassphrase", UNSET)

        skip_server_verification = d.pop("skipServerVerification", UNSET)

        ssh_config = cls(
            ssh_private_key=ssh_private_key,
            private_key_passphrase=private_key_passphrase,
            skip_server_verification=skip_server_verification,
        )

        return ssh_config

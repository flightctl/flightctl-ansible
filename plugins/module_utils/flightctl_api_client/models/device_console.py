from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceConsole")


@_attrs_define
class DeviceConsole:
    """
    Attributes:
        g_rpc_endpoint (str):
        session_id (str):
    """

    g_rpc_endpoint: str
    session_id: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        g_rpc_endpoint = self.g_rpc_endpoint

        session_id = self.session_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "gRPCEndpoint": g_rpc_endpoint,
                "sessionID": session_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        g_rpc_endpoint = d.pop("gRPCEndpoint")

        session_id = d.pop("sessionID")

        device_console = cls(
            g_rpc_endpoint=g_rpc_endpoint,
            session_id=session_id,
        )

        device_console.additional_properties = d
        return device_console

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

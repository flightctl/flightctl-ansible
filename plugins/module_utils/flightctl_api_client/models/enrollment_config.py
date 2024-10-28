from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.enrollment_service import EnrollmentService


T = TypeVar("T", bound="EnrollmentConfig")


@_attrs_define
class EnrollmentConfig:
    """
    Attributes:
        enrollment_service (EnrollmentService):
        grpc_management_endpoint (str):
    """

    enrollment_service: "EnrollmentService"
    grpc_management_endpoint: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        enrollment_service = self.enrollment_service.to_dict()

        grpc_management_endpoint = self.grpc_management_endpoint

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enrollment-service": enrollment_service,
                "grpc-management-endpoint": grpc_management_endpoint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.enrollment_service import EnrollmentService

        d = src_dict.copy()
        enrollment_service = EnrollmentService.from_dict(d.pop("enrollment-service"))

        grpc_management_endpoint = d.pop("grpc-management-endpoint")

        enrollment_config = cls(
            enrollment_service=enrollment_service,
            grpc_management_endpoint=grpc_management_endpoint,
        )

        enrollment_config.additional_properties = d
        return enrollment_config

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

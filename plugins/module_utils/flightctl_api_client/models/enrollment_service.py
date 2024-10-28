from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.enrollment_service_auth import EnrollmentServiceAuth
    from ..models.enrollment_service_service import EnrollmentServiceService


T = TypeVar("T", bound="EnrollmentService")


@_attrs_define
class EnrollmentService:
    """
    Attributes:
        authentication (EnrollmentServiceAuth):
        service (EnrollmentServiceService):
        enrollment_ui_endpoint (str):
    """

    authentication: "EnrollmentServiceAuth"
    service: "EnrollmentServiceService"
    enrollment_ui_endpoint: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        authentication = self.authentication.to_dict()

        service = self.service.to_dict()

        enrollment_ui_endpoint = self.enrollment_ui_endpoint

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authentication": authentication,
                "service": service,
                "enrollment-ui-endpoint": enrollment_ui_endpoint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.enrollment_service_auth import EnrollmentServiceAuth
        from ..models.enrollment_service_service import EnrollmentServiceService

        d = src_dict.copy()
        authentication = EnrollmentServiceAuth.from_dict(d.pop("authentication"))

        service = EnrollmentServiceService.from_dict(d.pop("service"))

        enrollment_ui_endpoint = d.pop("enrollment-ui-endpoint")

        enrollment_service = cls(
            authentication=authentication,
            service=service,
            enrollment_ui_endpoint=enrollment_ui_endpoint,
        )

        enrollment_service.additional_properties = d
        return enrollment_service

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

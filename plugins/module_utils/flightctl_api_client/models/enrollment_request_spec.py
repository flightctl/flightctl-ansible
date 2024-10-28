from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.device_status import DeviceStatus
    from ..models.enrollment_request_spec_labels import EnrollmentRequestSpecLabels


T = TypeVar("T", bound="EnrollmentRequestSpec")


@_attrs_define
class EnrollmentRequestSpec:
    """EnrollmentRequestSpec is a description of a EnrollmentRequest's target state.

    Attributes:
        csr (str): csr is a PEM-encoded PKCS#10 certificate signing request.
        device_status (Union[Unset, DeviceStatus]): DeviceStatus represents information about the status of a device.
            Status may trail the actual state of a device.
        labels (Union[Unset, EnrollmentRequestSpecLabels]): A set of labels that the service will apply to this device
            when its enrollment is approved
    """

    csr: str
    device_status: Union[Unset, "DeviceStatus"] = UNSET
    labels: Union[Unset, "EnrollmentRequestSpecLabels"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        csr = self.csr

        device_status: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.device_status, Unset):
            device_status = self.device_status.to_dict()

        labels: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.labels, Unset):
            labels = self.labels.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "csr": csr,
            }
        )
        if device_status is not UNSET:
            field_dict["deviceStatus"] = device_status
        if labels is not UNSET:
            field_dict["labels"] = labels

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.device_status import DeviceStatus
        from ..models.enrollment_request_spec_labels import EnrollmentRequestSpecLabels

        d = src_dict.copy()
        csr = d.pop("csr")

        _device_status = d.pop("deviceStatus", UNSET)
        device_status: Union[Unset, DeviceStatus]
        if isinstance(_device_status, Unset):
            device_status = UNSET
        else:
            device_status = DeviceStatus.from_dict(_device_status)

        _labels = d.pop("labels", UNSET)
        labels: Union[Unset, EnrollmentRequestSpecLabels]
        if isinstance(_labels, Unset):
            labels = UNSET
        else:
            labels = EnrollmentRequestSpecLabels.from_dict(_labels)

        enrollment_request_spec = cls(
            csr=csr,
            device_status=device_status,
            labels=labels,
        )

        enrollment_request_spec.additional_properties = d
        return enrollment_request_spec

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

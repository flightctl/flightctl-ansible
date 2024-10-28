import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.condition_status import ConditionStatus, check_condition_status
from ..models.condition_type import ConditionType, check_condition_type
from ..types import UNSET, Unset

T = TypeVar("T", bound="Condition")


@_attrs_define
class Condition:
    """Condition contains details for one aspect of the current state of this API Resource.

    Attributes:
        type (ConditionType):
        status (ConditionStatus):
        last_transition_time (datetime.datetime): The last time the condition transitioned from one status to another.
        message (str): Human readable message indicating details about last transition.
        reason (str): (brief) reason for the condition's last transition.
        observed_generation (Union[Unset, int]): The .metadata.generation that the condition was set based upon.
    """

    type: ConditionType
    status: ConditionStatus
    last_transition_time: datetime.datetime
    message: str
    reason: str
    observed_generation: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        type: str = self.type

        status: str = self.status

        last_transition_time = self.last_transition_time.isoformat()

        message = self.message

        reason = self.reason

        observed_generation = self.observed_generation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type,
                "status": status,
                "lastTransitionTime": last_transition_time,
                "message": message,
                "reason": reason,
            }
        )
        if observed_generation is not UNSET:
            field_dict["observedGeneration"] = observed_generation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        type = check_condition_type(d.pop("type"))

        status = check_condition_status(d.pop("status"))

        last_transition_time = isoparse(d.pop("lastTransitionTime"))

        message = d.pop("message")

        reason = d.pop("reason")

        observed_generation = d.pop("observedGeneration", UNSET)

        condition = cls(
            type=type,
            status=status,
            last_transition_time=last_transition_time,
            message=message,
            reason=reason,
            observed_generation=observed_generation,
        )

        condition.additional_properties = d
        return condition

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

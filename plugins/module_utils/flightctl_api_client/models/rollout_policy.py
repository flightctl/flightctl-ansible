from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.batch_sequence import BatchSequence
    from ..models.disruption_allowance import DisruptionAllowance


T = TypeVar("T", bound="RolloutPolicy")


@_attrs_define
class RolloutPolicy:
    """RolloutPolicy is the rollout policy of the fleet.

    Attributes:
        disruption_allowance (Union[Unset, DisruptionAllowance]): DisruptionAllowance defines the level of allowed
            disruption when rollout is in progress.
        device_selection (Union[Unset, BatchSequence]): BatchSequence defines the list of batches to be executed in
            sequence.
        success_threshold (Union[Unset, str]): Percentage is the string format representing percentage string.
        default_update_timeout (Union[Unset, str]): The maximum duration allowed for the action to complete.
            The duration should be specified as a positive integer
            followed by a time unit. Supported time units are:
            - 's' for seconds
            - 'm' for minutes
            - 'h' for hours
            - 'd' for days
    """

    disruption_allowance: Union[Unset, "DisruptionAllowance"] = UNSET
    device_selection: Union[Unset, "BatchSequence"] = UNSET
    success_threshold: Union[Unset, str] = UNSET
    default_update_timeout: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        disruption_allowance: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.disruption_allowance, Unset):
            disruption_allowance = self.disruption_allowance.to_dict()

        device_selection: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.device_selection, Unset):
            device_selection = self.device_selection.to_dict()

        success_threshold = self.success_threshold

        default_update_timeout = self.default_update_timeout

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if disruption_allowance is not UNSET:
            field_dict["disruptionAllowance"] = disruption_allowance
        if device_selection is not UNSET:
            field_dict["deviceSelection"] = device_selection
        if success_threshold is not UNSET:
            field_dict["successThreshold"] = success_threshold
        if default_update_timeout is not UNSET:
            field_dict["defaultUpdateTimeout"] = default_update_timeout

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.batch_sequence import BatchSequence
        from ..models.disruption_allowance import DisruptionAllowance

        d = src_dict.copy()
        _disruption_allowance = d.pop("disruptionAllowance", UNSET)
        disruption_allowance: Union[Unset, DisruptionAllowance]
        if isinstance(_disruption_allowance, Unset):
            disruption_allowance = UNSET
        else:
            disruption_allowance = DisruptionAllowance.from_dict(_disruption_allowance)

        _device_selection = d.pop("deviceSelection", UNSET)
        device_selection: Union[Unset, BatchSequence]
        if isinstance(_device_selection, Unset):
            device_selection = UNSET
        else:
            device_selection = BatchSequence.from_dict(_device_selection)

        success_threshold = d.pop("successThreshold", UNSET)

        default_update_timeout = d.pop("defaultUpdateTimeout", UNSET)

        rollout_policy = cls(
            disruption_allowance=disruption_allowance,
            device_selection=device_selection,
            success_threshold=success_threshold,
            default_update_timeout=default_update_timeout,
        )

        rollout_policy.additional_properties = d
        return rollout_policy

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

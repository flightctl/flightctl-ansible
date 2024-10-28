from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.application_env_vars_env_vars import ApplicationEnvVarsEnvVars


T = TypeVar("T", bound="ApplicationEnvVars")


@_attrs_define
class ApplicationEnvVars:
    """
    Attributes:
        env_vars (Union[Unset, ApplicationEnvVarsEnvVars]): Environment variable key-value pairs, injected during
            runtime
    """

    env_vars: Union[Unset, "ApplicationEnvVarsEnvVars"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        env_vars: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.env_vars, Unset):
            env_vars = self.env_vars.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if env_vars is not UNSET:
            field_dict["envVars"] = env_vars

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.application_env_vars_env_vars import ApplicationEnvVarsEnvVars

        d = src_dict.copy()
        _env_vars = d.pop("envVars", UNSET)
        env_vars: Union[Unset, ApplicationEnvVarsEnvVars]
        if isinstance(_env_vars, Unset):
            env_vars = UNSET
        else:
            env_vars = ApplicationEnvVarsEnvVars.from_dict(_env_vars)

        application_env_vars = cls(
            env_vars=env_vars,
        )

        application_env_vars.additional_properties = d
        return application_env_vars

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

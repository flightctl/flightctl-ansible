from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="HookActionExecutable")


@_attrs_define
class HookActionExecutable:
    """
    Attributes:
        run (str): The command to be executed, including any arguments using standard shell syntax. This field supports
            multiple commands piped together, as if they were executed under a bash -c context.
        env_vars (Union[Unset, List[str]]): An optional list of KEY=VALUE pairs to set as environment variables for the
            executable.
        work_dir (Union[Unset, str]): The directory in which the executable will be run from if it is left empty it will
            run from the users home directory.
    """

    run: str
    env_vars: Union[Unset, List[str]] = UNSET
    work_dir: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        run = self.run

        env_vars: Union[Unset, List[str]] = UNSET
        if not isinstance(self.env_vars, Unset):
            env_vars = self.env_vars

        work_dir = self.work_dir

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run": run,
            }
        )
        if env_vars is not UNSET:
            field_dict["envVars"] = env_vars
        if work_dir is not UNSET:
            field_dict["workDir"] = work_dir

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        run = d.pop("run")

        env_vars = cast(List[str], d.pop("envVars", UNSET))

        work_dir = d.pop("workDir", UNSET)

        hook_action_executable = cls(
            run=run,
            env_vars=env_vars,
            work_dir=work_dir,
        )

        hook_action_executable.additional_properties = d
        return hook_action_executable

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

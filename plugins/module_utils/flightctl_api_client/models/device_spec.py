from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.application_spec import ApplicationSpec
    from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
    from ..models.device_hooks_spec import DeviceHooksSpec
    from ..models.device_os_spec import DeviceOSSpec
    from ..models.device_spec_systemd import DeviceSpecSystemd
    from ..models.disk_resource_monitor_spec import DiskResourceMonitorSpec
    from ..models.git_config_provider_spec import GitConfigProviderSpec
    from ..models.http_config_provider_spec import HttpConfigProviderSpec
    from ..models.inline_config_provider_spec import InlineConfigProviderSpec
    from ..models.kubernetes_secret_provider_spec import KubernetesSecretProviderSpec
    from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec


T = TypeVar("T", bound="DeviceSpec")


@_attrs_define
class DeviceSpec:
    """
    Attributes:
        os (Union[Unset, DeviceOSSpec]):
        config (Union[Unset, List[Union['GitConfigProviderSpec', 'HttpConfigProviderSpec', 'InlineConfigProviderSpec',
            'KubernetesSecretProviderSpec']]]): List of config providers.
        hooks (Union[Unset, DeviceHooksSpec]):
        applications (Union[Unset, List['ApplicationSpec']]): List of applications.
        systemd (Union[Unset, DeviceSpecSystemd]):
        resources (Union[Unset, List[Union['CPUResourceMonitorSpec', 'DiskResourceMonitorSpec',
            'MemoryResourceMonitorSpec']]]): Array of resource monitor configurations.
    """

    os: Union[Unset, "DeviceOSSpec"] = UNSET
    config: Union[
        Unset,
        List[
            Union[
                "GitConfigProviderSpec",
                "HttpConfigProviderSpec",
                "InlineConfigProviderSpec",
                "KubernetesSecretProviderSpec",
            ]
        ],
    ] = UNSET
    hooks: Union[Unset, "DeviceHooksSpec"] = UNSET
    applications: Union[Unset, List["ApplicationSpec"]] = UNSET
    systemd: Union[Unset, "DeviceSpecSystemd"] = UNSET
    resources: Union[
        Unset,
        List[
            Union[
                "CPUResourceMonitorSpec",
                "DiskResourceMonitorSpec",
                "MemoryResourceMonitorSpec",
            ]
        ],
    ] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
        from ..models.git_config_provider_spec import GitConfigProviderSpec
        from ..models.inline_config_provider_spec import InlineConfigProviderSpec
        from ..models.kubernetes_secret_provider_spec import (
            KubernetesSecretProviderSpec,
        )
        from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec

        os: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.os, Unset):
            os = self.os.to_dict()

        config: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.config, Unset):
            config = []
            for config_item_data in self.config:
                config_item: Dict[str, Any]
                if isinstance(config_item_data, GitConfigProviderSpec):
                    config_item = config_item_data.to_dict()
                elif isinstance(config_item_data, KubernetesSecretProviderSpec):
                    config_item = config_item_data.to_dict()
                elif isinstance(config_item_data, InlineConfigProviderSpec):
                    config_item = config_item_data.to_dict()
                else:
                    config_item = config_item_data.to_dict()

                config.append(config_item)

        hooks: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.hooks, Unset):
            hooks = self.hooks.to_dict()

        applications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.applications, Unset):
            applications = []
            for applications_item_data in self.applications:
                applications_item = applications_item_data.to_dict()
                applications.append(applications_item)

        systemd: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.systemd, Unset):
            systemd = self.systemd.to_dict()

        resources: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.resources, Unset):
            resources = []
            for resources_item_data in self.resources:
                resources_item: Dict[str, Any]
                if isinstance(resources_item_data, CPUResourceMonitorSpec):
                    resources_item = resources_item_data.to_dict()
                elif isinstance(resources_item_data, MemoryResourceMonitorSpec):
                    resources_item = resources_item_data.to_dict()
                else:
                    resources_item = resources_item_data.to_dict()

                resources.append(resources_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if os is not UNSET:
            field_dict["os"] = os
        if config is not UNSET:
            field_dict["config"] = config
        if hooks is not UNSET:
            field_dict["hooks"] = hooks
        if applications is not UNSET:
            field_dict["applications"] = applications
        if systemd is not UNSET:
            field_dict["systemd"] = systemd
        if resources is not UNSET:
            field_dict["resources"] = resources

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.application_spec import ApplicationSpec
        from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
        from ..models.device_hooks_spec import DeviceHooksSpec
        from ..models.device_os_spec import DeviceOSSpec
        from ..models.device_spec_systemd import DeviceSpecSystemd
        from ..models.disk_resource_monitor_spec import DiskResourceMonitorSpec
        from ..models.git_config_provider_spec import GitConfigProviderSpec
        from ..models.http_config_provider_spec import HttpConfigProviderSpec
        from ..models.inline_config_provider_spec import InlineConfigProviderSpec
        from ..models.kubernetes_secret_provider_spec import (
            KubernetesSecretProviderSpec,
        )
        from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec

        d = src_dict.copy()
        _os = d.pop("os", UNSET)
        os: Union[Unset, DeviceOSSpec]
        if isinstance(_os, Unset):
            os = UNSET
        else:
            os = DeviceOSSpec.from_dict(_os)

        config = []
        _config = d.pop("config", UNSET)
        for config_item_data in _config or []:

            def _parse_config_item(
                data: object,
            ) -> Union[
                "GitConfigProviderSpec",
                "HttpConfigProviderSpec",
                "InlineConfigProviderSpec",
                "KubernetesSecretProviderSpec",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_config_provider_spec_type_0 = (
                        GitConfigProviderSpec.from_dict(data)
                    )

                    return componentsschemas_config_provider_spec_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_config_provider_spec_type_1 = (
                        KubernetesSecretProviderSpec.from_dict(data)
                    )

                    return componentsschemas_config_provider_spec_type_1
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_config_provider_spec_type_2 = (
                        InlineConfigProviderSpec.from_dict(data)
                    )

                    return componentsschemas_config_provider_spec_type_2
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_config_provider_spec_type_3 = (
                    HttpConfigProviderSpec.from_dict(data)
                )

                return componentsschemas_config_provider_spec_type_3

            config_item = _parse_config_item(config_item_data)

            config.append(config_item)

        _hooks = d.pop("hooks", UNSET)
        hooks: Union[Unset, DeviceHooksSpec]
        if isinstance(_hooks, Unset):
            hooks = UNSET
        else:
            hooks = DeviceHooksSpec.from_dict(_hooks)

        applications = []
        _applications = d.pop("applications", UNSET)
        for applications_item_data in _applications or []:
            applications_item = ApplicationSpec.from_dict(applications_item_data)

            applications.append(applications_item)

        _systemd = d.pop("systemd", UNSET)
        systemd: Union[Unset, DeviceSpecSystemd]
        if isinstance(_systemd, Unset):
            systemd = UNSET
        else:
            systemd = DeviceSpecSystemd.from_dict(_systemd)

        resources = []
        _resources = d.pop("resources", UNSET)
        for resources_item_data in _resources or []:

            def _parse_resources_item(
                data: object,
            ) -> Union[
                "CPUResourceMonitorSpec",
                "DiskResourceMonitorSpec",
                "MemoryResourceMonitorSpec",
            ]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_resource_monitor_type_0 = (
                        CPUResourceMonitorSpec.from_dict(data)
                    )

                    return componentsschemas_resource_monitor_type_0
                except:  # noqa: E722
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    componentsschemas_resource_monitor_type_1 = (
                        MemoryResourceMonitorSpec.from_dict(data)
                    )

                    return componentsschemas_resource_monitor_type_1
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                componentsschemas_resource_monitor_type_2 = (
                    DiskResourceMonitorSpec.from_dict(data)
                )

                return componentsschemas_resource_monitor_type_2

            resources_item = _parse_resources_item(resources_item_data)

            resources.append(resources_item)

        device_spec = cls(
            os=os,
            config=config,
            hooks=hooks,
            applications=applications,
            systemd=systemd,
            resources=resources,
        )

        device_spec.additional_properties = d
        return device_spec

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

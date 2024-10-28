from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
    from ..models.device_console import DeviceConsole
    from ..models.device_hooks_spec import DeviceHooksSpec
    from ..models.device_os_spec import DeviceOSSpec
    from ..models.disk_resource_monitor_spec import DiskResourceMonitorSpec
    from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec
    from ..models.rendered_application_spec import RenderedApplicationSpec
    from ..models.rendered_device_spec_containers import RenderedDeviceSpecContainers
    from ..models.rendered_device_spec_systemd import RenderedDeviceSpecSystemd


T = TypeVar("T", bound="RenderedDeviceSpec")


@_attrs_define
class RenderedDeviceSpec:
    """
    Attributes:
        rendered_version (str):
        os (Union[Unset, DeviceOSSpec]):
        containers (Union[Unset, RenderedDeviceSpecContainers]):
        config (Union[Unset, str]):
        applications (Union[Unset, List['RenderedApplicationSpec']]):
        hooks (Union[Unset, DeviceHooksSpec]):
        systemd (Union[Unset, RenderedDeviceSpecSystemd]):
        resources (Union[Unset, List[Union['CPUResourceMonitorSpec', 'DiskResourceMonitorSpec',
            'MemoryResourceMonitorSpec']]]): Array of resource monitor configurations.
        console (Union[Unset, DeviceConsole]):
    """

    rendered_version: str
    os: Union[Unset, "DeviceOSSpec"] = UNSET
    containers: Union[Unset, "RenderedDeviceSpecContainers"] = UNSET
    config: Union[Unset, str] = UNSET
    applications: Union[Unset, List["RenderedApplicationSpec"]] = UNSET
    hooks: Union[Unset, "DeviceHooksSpec"] = UNSET
    systemd: Union[Unset, "RenderedDeviceSpecSystemd"] = UNSET
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
    console: Union[Unset, "DeviceConsole"] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
        from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec

        rendered_version = self.rendered_version

        os: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.os, Unset):
            os = self.os.to_dict()

        containers: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.containers, Unset):
            containers = self.containers.to_dict()

        config = self.config

        applications: Union[Unset, List[Dict[str, Any]]] = UNSET
        if not isinstance(self.applications, Unset):
            applications = []
            for applications_item_data in self.applications:
                applications_item = applications_item_data.to_dict()
                applications.append(applications_item)

        hooks: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.hooks, Unset):
            hooks = self.hooks.to_dict()

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

        console: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.console, Unset):
            console = self.console.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "renderedVersion": rendered_version,
            }
        )
        if os is not UNSET:
            field_dict["os"] = os
        if containers is not UNSET:
            field_dict["containers"] = containers
        if config is not UNSET:
            field_dict["config"] = config
        if applications is not UNSET:
            field_dict["applications"] = applications
        if hooks is not UNSET:
            field_dict["hooks"] = hooks
        if systemd is not UNSET:
            field_dict["systemd"] = systemd
        if resources is not UNSET:
            field_dict["resources"] = resources
        if console is not UNSET:
            field_dict["console"] = console

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.cpu_resource_monitor_spec import CPUResourceMonitorSpec
        from ..models.device_console import DeviceConsole
        from ..models.device_hooks_spec import DeviceHooksSpec
        from ..models.device_os_spec import DeviceOSSpec
        from ..models.disk_resource_monitor_spec import DiskResourceMonitorSpec
        from ..models.memory_resource_monitor_spec import MemoryResourceMonitorSpec
        from ..models.rendered_application_spec import RenderedApplicationSpec
        from ..models.rendered_device_spec_containers import (
            RenderedDeviceSpecContainers,
        )
        from ..models.rendered_device_spec_systemd import RenderedDeviceSpecSystemd

        d = src_dict.copy()
        rendered_version = d.pop("renderedVersion")

        _os = d.pop("os", UNSET)
        os: Union[Unset, DeviceOSSpec]
        if isinstance(_os, Unset):
            os = UNSET
        else:
            os = DeviceOSSpec.from_dict(_os)

        _containers = d.pop("containers", UNSET)
        containers: Union[Unset, RenderedDeviceSpecContainers]
        if isinstance(_containers, Unset):
            containers = UNSET
        else:
            containers = RenderedDeviceSpecContainers.from_dict(_containers)

        config = d.pop("config", UNSET)

        applications = []
        _applications = d.pop("applications", UNSET)
        for applications_item_data in _applications or []:
            applications_item = RenderedApplicationSpec.from_dict(
                applications_item_data
            )

            applications.append(applications_item)

        _hooks = d.pop("hooks", UNSET)
        hooks: Union[Unset, DeviceHooksSpec]
        if isinstance(_hooks, Unset):
            hooks = UNSET
        else:
            hooks = DeviceHooksSpec.from_dict(_hooks)

        _systemd = d.pop("systemd", UNSET)
        systemd: Union[Unset, RenderedDeviceSpecSystemd]
        if isinstance(_systemd, Unset):
            systemd = UNSET
        else:
            systemd = RenderedDeviceSpecSystemd.from_dict(_systemd)

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

        _console = d.pop("console", UNSET)
        console: Union[Unset, DeviceConsole]
        if isinstance(_console, Unset):
            console = UNSET
        else:
            console = DeviceConsole.from_dict(_console)

        rendered_device_spec = cls(
            rendered_version=rendered_version,
            os=os,
            containers=containers,
            config=config,
            applications=applications,
            hooks=hooks,
            systemd=systemd,
            resources=resources,
            console=console,
        )

        rendered_device_spec.additional_properties = d
        return rendered_device_spec

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

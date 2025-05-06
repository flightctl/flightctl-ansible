# coding: utf-8

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function, annotations)

__metaclass__ = type

DOCUMENTATION = r'''---
plugin: flightctl.core.flightctl
version_added: "0.5.0"
plugin_type: inventory
short_description: Returns Ansible inventory using Flight Control as source.
description: |
  - Returns Ansible inventory  using Flight Control as source.
  - Uses the same API as other modules in this collection.
  - The plugin uses collection's API.
  - You can reuse parameters by supplying a flightctl_config_file. It will override current parameters
options:
    plugin:
      description: Name of the plugin
      required: false
      choices:
        - flightctl.core.flightctl
    ca_path:
      description: Path to a CA cert file to use when making requests.
      default: null
      type: path
    ca_data:
      description: CertificateAuthorityData contains PEM-encoded certificate authority certificates.
                            It will be written into a temporary file to enable underlying code to use ca_path.
      default: null
      type: path
    verify_ssl:
      description: Whether to allow insecure connections to Flight Control service.
                            If `false', SSL certificates will not be validated.
                            This should only be used on personally controlled sites using self-signed certificates.
      default: True
      type: bool
    host:
      description: URL to Flight Control server. A token or username/password must be also provided.
      default: null
      type: path
    username:
      description: Username for your Flight Control service. Please note that this only works with proxies configured to use HTTP Basic Auth.
      default: null
      type: str
    password:
      description: Password for your Flight Control service. Please note that this only works with proxies configured to use HTTP Basic Auth.
      default: null
      type: str
    token:
      description: The Flight Control API token to use.
      default: null
      type: str
    additional_groups:
      description: Additional groups to add devices to.
      type: list
      elements: dict
      options:
        name:
          description: Group name (should be unique)
          type: str
          required: true
        label_selectors:
          description: list of label selectors in format "key = value" or "key != value"
          type: list
          elements: str
          default: []
        field_selectors:
          description: |
            list of field selectors in format "field <op> value" to be matched against fields,
            where <op> is one of != == = >= <= > < in notin contains notcontains ! notexists
          type: list
          elements: str
          default: []
      default: []
      required: false
    request_timeout:
      description: |
        - Specify the timeout (in seconds) Ansible should use in requests to the controller host.
        - Defaults to 120 sec (i.e. 2 min), but this is handled by the shared module_utils code.
      type: float
      default: 120.0
    flightctl_config_file:
      description: Path to the config file.
                        host, username, password, token, ca_path and ca_data will be taken from there.
      type: path
'''

"""
In order to add cacheing in a future:
1. Add parameters to configuration
cache:
  description:
      - Enable inventory caching for this plugin.
      type: bool
      default: False
  cache_timeout:
      description:
          - Number of seconds before a cache entry expires.
      type: int
      default: 0

2. Import Cacheable and add it to class InventoryModule
  from ansible.plugins.inventory import Cacheable

3. Make parameter cache of parse() to have default True

4. Handle cache eviction in parse() after self._read_config_data(path)
   cache_timeout = self.get_option('cache_timeout') or 0
   if cache_timeout:
       # enable caching and override the timeout
       # flip on cache and set the TTL
       self.set_option('cache', True)
       self.set_option('cache_timeout', cache_timeout)
   else:
       # no timeout → disable caching entirely and drop any old entries
       self.set_option('cache', False)
       self._cache.clear()
   # Get cache key
   cache_key = self.get_cache_key(path)
   # Check if cache is active && we got a valid cache entry
   if cache_timeout and cache and cache_key in self._cache:
       self._display.warning('populated from cache')
       self._populate_from_cache(self._cache[cache_key])
       return

5. After fetching inventory store it in cache
   if cache_timeout:
       self._cache[cache_key] = inventory_data

6. Uncomment _populate_from_cache function
"""

try:
    # APIs
    from flightctl.api_client import ApiClient
    from flightctl.api.device_api import DeviceApi
    from flightctl.api.fleet_api import FleetApi

    # Configuration
    from flightctl.configuration import Configuration

    # Models
    from flightctl.models.device_list import DeviceList
    from flightctl.models.fleet_list import FleetList
except ImportError as imp_exc:
    CLIENT_IMPORT_ERROR = imp_exc
else:
    CLIENT_IMPORT_ERROR = None

from ..module_utils.config_loader import ConfigLoader
from ..module_utils.exceptions import ValidationException, FlightctlApiException, FlightctlException
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.module_utils.basic import AnsibleModule
from ansible.utils.display import Display
from contextlib import contextmanager
import re
import base64
import tempfile
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    TypeAlias,
    Generator,
)

T = TypeVar('T')
LabelsType: TypeAlias = Dict[str, str]
AdditionalGroupInfoType: TypeAlias = Dict[str, Tuple[str, str]]


class InventoryModule(BaseInventoryPlugin, Constructable, AnsibleModule):
    NAME = 'flightctl.core.flightctl'  # used internally by Ansible, must match the filename

    LIMIT_PER_PAGE: int = 1000

    def __init__(self, *args, **kwargs):
        self.config = None
        if CLIENT_IMPORT_ERROR:
            raise CLIENT_IMPORT_ERROR
        super(InventoryModule, self).__init__(*args, **kwargs)
        self.inventory_data: Dict[str, Any] = {
            'hosts': {},  # A mapping of hostname → host‑vars dict, for example
            # hosts = {
            #   "device‑123": {
            #     "id": "device‑123",
            #     "device_type": "router",
            #     "netIpDefault": "10.0.0.5",
            #     "ansible_host": "10.0.0.5",
            #     # …any other properties you pulled from the API…
            #   },
            #   "device‑456": { … },
            #   # …
            # }
            'groups': {}  # A mapping of group name → group‑data dict, where
            # - The group‑data dict must include at least a "hosts" key whose value is a list of
            #   hostnames that belong to that group. Group "all" is maintained by Ansible. It is
            #   required when we want to attach group-vars to "all" or to get them first in `--list`
            #
            #   groups = {
            #     "fleet1": {
            #       "hosts": ["device‑123", "device‑789"]
            #     },
            #     "all": {
            #       "hosts": ["device‑123","device‑456","device‑789"]
            #     }
            #   }
            # - It can also supply a "vars" key in there if you need group‑level variables
            #   groups["mygroup"]["vars"] = { "some_var": 42 }
        }
        self._display = Display(verbosity=3)

    def verify_file(self, path: str) -> bool:
        """ Verify that the source file can be processed correctly. """
        if super(InventoryModule, self).verify_file(path):
            # Checking if file ends with 'inventory.yml' or 'inventory.yaml'
            valid_extensions = ('inventory.yml', 'inventory.yaml')
            return path.endswith(valid_extensions)
        self._display.error('Skipping due to inventory source not ending in "inventory.yaml" nor "inventory.yml"')
        return False

    def parse(self, inventory: Any, loader: Any, path: str, cache: bool = False) -> None:
        """ Parse the inventory file. """
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Load configuration parameters from the inventory file
        self._read_config_data(path)
        self.config = self._setup_connection_configuration()

        # Fetch devices and fleets
        devices, fleets = _get_devices_and_fleets(self.config, self.LIMIT_PER_PAGE)

        # Process devices and fleets to inventory data
        # This dict will be used to populate cache
        self._populate_inventory_devices(devices)
        self._populate_inventory_fleets(fleets, self.config)
        self._populate_inventory_additional_groups(additional_groups=self.get_option('additional_groups'))

    def _load_config_file(self) -> ConfigLoader | None:
        """ Load configuration files using ConfigLoader. """
        config_file = self.get_option("flightctl_config_file") or self.get_option("config_file")
        if not config_file:
            return None

        try:
            # Use ConfigLoader to load config from file or fallback to defaults
            return ConfigLoader(config_file=config_file)
        except Exception as e:
            raise FlightctlException(f"Failed to load the config file: {e}") from e

    def _create_tmp_crt(self, encoded_data):
        decoded_data = base64.b64decode(encoded_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix="crt") as temp_file:
            # Write our decoded data to a .crt file and point our ca_path to the filename
            temp_file.write(decoded_data)
            temp_file.flush()
            self.ca_path = temp_file.name

            # Ensure the created temp file is deleted when our module exits
            self.add_cleanup_file(temp_file.name)

    def _setup_connection_configuration(self) -> Configuration:
        """
        Read Flight Control's config file if supplied.
        Override values with those supplied in an inventory setup
        """
        config_file: ConfigLoader = self._load_config_file()
        host = (self.get_option('host', None)
                or getattr(config_file, 'host', None))
        if not host:
            raise ValidationException("host is required in inventory mode")
        verify_ssl = self.get_option('verify_ssl', None)
        if verify_ssl is None:
            verify_ssl = (getattr(config_file, 'verify_ssl', None)
                          or getattr(config_file, 'flightctl_verify_ssl', None))
        if verify_ssl is None:
            verify_ssl = False
        access_token = (self.get_option('token', None)
                        or getattr(config_file, 'token', None))
        username = (self.get_option('username', None)
                    or getattr(config_file, 'username', None))
        password = (self.get_option('password', None)
                    or getattr(config_file, 'password', None))
        if verify_ssl and not (access_token or (username and password)):
            raise ValidationException(
                "Authentication is required: provide either access_token or both username and password")

        ca_path = (self.get_option('ca_path', None)
                   or getattr(config_file, 'ca_path', None)
                   or getattr(config_file, 'flightctl_ca_path', None))
        # Special case - when we have loaded certificate authority data that needs to be written
        # to a file so our underlying requests library can use it
        if not ca_path and hasattr(config_file, "ca_data"):
            self._create_tmp_crt(getattr(config_file, "ca_data"))
            ca_path = self.ca_path

        request_timeout = self.get_option('request_timeout', 120.0)

        config = Configuration(
            host=host,
            access_token=access_token,
            username=username,
            password=password,
            ssl_ca_cert=ca_path,
        )
        config.request_timeout = request_timeout
        config.verify_ssl = verify_ssl
        return config

    def _populate_inventory_fleets(self, fleets: List[Any], config) -> None:
        """
        Given lists of fleets, populate self.inventory groups.
        - fleets: list of fleets
        """
        if len(fleets) == 0:
            return

        for fleet in [fleet.to_dict() for fleet in fleets]:
            fleet_id = _validate_fleet(fleet)
            devices = _fetch_fleet_devices(fleet_id, config, self.LIMIT_PER_PAGE) or []
            for device in [device.to_dict() for device in devices]:
                device_id, metadata = _validate_device(device)
                self._add_to_group(fleet_id, device_id)

    def _populate_inventory_devices(self, devices: List[Any]) -> None:
        """
        Given lists of devices, populate self.inventory and return the full inventory_data dict.
        - devices: list of device instances
        """
        if len(devices) == 0:
            return

        # Process devices
        for device in [device.to_dict() for device in devices]:
            device_id, metadata = _validate_device(device)

            # add host
            self.inventory.add_host(device_id)  # Add host to Ansible inventory
            self.inventory_data['hosts'][device_id] = device.copy()

            # add host variables
            for key, value in device.items():
                if key != 'custom_vars':  # Handle custom vars separately
                    self.inventory.set_variable(device_id, key, value)
                    self.inventory_data['hosts'][device_id][key] = value

            # Add any custom variables
            if 'custom_vars' in device and isinstance(device['custom_vars'], dict):
                for var_name, var_value in device['custom_vars'].items():
                    self.inventory.set_variable(device_id, var_name, var_value)
                    self.inventory_data['hosts'][device_id][var_name] = var_value

            # Set ansible_host if netIpDefault is available
            net_ip_default = (
                device.get('status', {})
                .get('systemInfo', {})
                .get('netIpDefault')
            )
            if net_ip_default:
                self.inventory.set_variable(device_id, 'ansible_host', net_ip_default)
                self.inventory_data['hosts'][device_id]['ansible_host'] = net_ip_default

    def _populate_inventory_additional_groups(self, additional_groups: List[Dict[str, Any]]) -> None:
        """
        Given lists of additional_groups, populate self.inventory

        - additional_groups: list of dicts with keys 'name', 'label_selectors', 'field_selectors'
        """
        # handle additional groups
        additional_groups_info = _prepare_additional_groups_info(additional_groups)
        for group_name, selectors in additional_groups_info.items():
            label_selectors, field_selectors = selectors
            devices = _get_devices_by_labels_and_fields(self.config, label_selectors, field_selectors,
                                                        self.LIMIT_PER_PAGE, group_name)
            for device in [device.to_dict() for device in devices]:
                device_id, metadata = _validate_device(device)
                self._add_to_group(group_name, device_id)

    def _add_to_group(self, group_name: str, device_id: str):
        """ Add a host into the given group (creating it if necessary) """
        group_name = _sanitize_group_name(group_name)
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)
            self.inventory_data['groups'][group_name] = {'hosts': []}
        self.inventory.add_child(group_name, device_id)
        self.inventory_data['groups'][group_name]['hosts'].append(device_id)


# ---------------------- Custom context manager ------------------
@contextmanager
def flightctl_apis(config: Configuration) -> Generator[tuple[DeviceApi, FleetApi], Any, None]:
    """ Context manager yielding both API clients (device_api, fleet_api) """
    with ApiClient(configuration=config) as client:
        yield DeviceApi(client), FleetApi(client)


# ---------------------- Static methods ------------------
def _get_data(
        list_func: Callable[..., Any],
        label_list: str | None,
        field_list: str | None,
        limit: int | None = 1000
) -> List[T]:
    """ Repeatedly call `list_func` until exhausted; return combined list """
    all_records: list[T] = []
    continue_token: Optional[str] = None

    while True:
        try:
            # Call list_devices passing the continuation token and other parameters
            response = list_func(
                var_continue=continue_token,  # Pass the current continuation token, if any
                label_selector=label_list,
                field_selector=field_list,
                limit=limit
            )
        except Exception as e:
            raise FlightctlApiException(f"Error retrieving data from FlightCTL API: {e}") from e
        records: Sequence[T] = response.items
        all_records.extend(records)
        metadata = response.to_dict().get('metadata', {})
        continue_token = metadata.get("continue", None)

        if not continue_token:
            break

    return all_records


def _fetch_fleet_devices(fleet_id: str, config, limit_per_page: int) -> List[Any]:
    """ Retrieve devices belonging to a fleet """
    _display = Display()
    field_list = f"metadata.owner = Fleet/{fleet_id}"
    with flightctl_apis(config) as (device_api, fleet_api):
        devices = _get_data(device_api.list_devices, label_list=None, field_list=field_list, limit=limit_per_page)
        _display.warning(f"Retrieved total of {len(devices)} devices from fleet {fleet_id}")
    return devices


def _sanitize_group_name(group_name: str) -> str:
    """ Turn invalid characters (.-/) into underscores and strip any path prefix. """
    group_name = re.sub(r'[-.]', '_', group_name)
    return re.sub(r'^.*/', '', group_name)


def _prepare_additional_groups_info(additional_groups: List[Dict[str, Any]]) -> AdditionalGroupInfoType:
    """
    Validate & normalize the additional_groups list from the inventory YAML.
    Each entry must have at least one non-empty fleet/label_selectors/field_selectors:
      - 'name': str
      - 'label_selector': List[str]
      - 'field_selector': List[str]
    """

    display = Display()

    supported_field_selectors = tuple(["metadata.alias",
                                       "metadata.creationTimestamp",
                                       "metadata.name",
                                       "metadata.nameOrAlias",
                                       "metadata.owner",
                                       "status.applicationsSummary.status",
                                       "status.lastSeen",
                                       "status.lifecycle.status",
                                       "status.summary.status",
                                       "status.updated.status",
                                       ])

    additional_groups_info: AdditionalGroupInfoType = {}
    for group_cfg in additional_groups:
        group_name = group_cfg.get('name', "")
        if group_name == "":
            display.error(f"additional_group {group_cfg} must contain a non-empty name")
            continue

        # Process label_selectors
        lbl_sel = group_cfg.get("label_selectors", [])
        # Type-guard: must be list of dicts
        if not isinstance(lbl_sel, list):
            continue
        # Join all label selectors into a comma-separated string
        label_selectors: str | None = ",".join(lbl_sel)

        fld_sel = group_cfg.get("field_selectors", [])
        if not all(selector.startswith(supported_field_selectors) for selector in fld_sel):
            display.error(f"additional group {group_name} must contain only supported field_selectors, {fld_sel} found")
            continue
        # Join all field selectors into a comma-separated string
        field_selectors: str | None = ",".join(fld_sel)

        if not label_selectors and not field_selectors:
            continue

        if label_selectors:
            label_selectors = remove_quotes(label_selectors)
        if field_selectors:
            field_selectors = remove_quotes(field_selectors)
        additional_groups_info[group_name] = (label_selectors, field_selectors)

    return additional_groups_info


def _validate_device(device):
    """ Validate device has required structure """
    metadata = device.get('metadata', None)
    if not metadata:
        raise ValidationException(f"device {device} got an invalid structure")
    # Use device name or host name as the Ansible inventory hostname
    device_id = metadata.get('name', None)
    if not device_id:
        device_id = device.get('status', None) and device.get('systemInfo', None) and device.get('hostname', None)
    if not device_id:
        raise ValidationException(f"device {device} got neither name nor hostname")
    return device_id, metadata


def _validate_fleet(fleet) -> str:
    """ Validate device has required structure """
    metadata = fleet.get('metadata', None)
    if not metadata:
        raise ValidationException(f"fleet {fleet} got an invalid structure")
    fleet_id = metadata.get('name', None)
    if not fleet_id:
        raise ValidationException(f"fleet {fleet} got no name")
    return fleet_id


def remove_quotes(text):
    """ Remove double and single quotes """
    return text.replace("'", "").replace('"', "")


def _get_devices_and_fleets(config, limit_per_page: int) -> Tuple[List[DeviceList], List[FleetList]]:
    """
    Fetch all devices and fleets from Flight Control.
    Group devices according to fleets and additional groups.
    Note: Device may present in many groups
    """
    _display = Display()
    with flightctl_apis(config) as (device_api, fleet_api):
        # We're **always** fetching a full list of devices and fleets
        all_devices = _get_data(device_api.list_devices, label_list=None, field_list=None, limit=limit_per_page)
        _display.warning(f"Retrieved total of {len(all_devices)} devices")

        all_fleets = _get_data(fleet_api.list_fleets, label_list=None, field_list=None, limit=limit_per_page)
        _display.warning(f"Retrieved total of {len(all_fleets)} fleets")

    return all_devices, all_fleets


def _get_devices_by_labels_and_fields(config, label_list: str, field_list: str, limit_per_page: int,
                                      group_name: str) -> List[DeviceList]:
    """ Fetch all devices from Flight Control than got these labels and fields """
    _display = Display()
    with flightctl_apis(config) as (device_api, fleet_api):
        devices = _get_data(device_api.list_devices,
                            label_list=label_list, field_list=field_list, limit=limit_per_page)
        _display.warning(
            f"Retrieved total of {len(devices)} devices for group {group_name} by labels {label_list} and fields {field_list}")

    return devices

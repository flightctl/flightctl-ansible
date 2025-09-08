# coding: utf-8

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function, annotations)

__metaclass__ = type

DOCUMENTATION = r'''---
name: flightctl
version_added: "0.7.0"
short_description: Returns Ansible inventory using Flight Control as source.
description:
  - Returns Ansible inventory using Flight Control as source.
  - Uses the same API as other modules in this collection.
  - The plugin uses collection's API.
  - You can optionally supply a C(flightctl_config_file) pointing to the FlightCtl
    config file (for example, C(~/.config/flightctl/client.yaml)). Values specified
    in the inventory override values loaded from that file.
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
      type: bool
    host:
      description: URL to Flight Control server. A token or username/password must be also provided.
      default: null
      type: str
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
      suboptions:
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
      description: |
        - Path to the FlightCtl config file (for example, C(~/.config/flightctl/client.yaml)).
        - Reads the following keys from that file: C(authentication.token),
          C(service.server), C(service.insecureSkipVerify), and
          C(service.certificate-authority-data) (base64-encoded PEM).
        - Any values defined in the inventory override values from this file.
      type: path
requirements:
    - "python >= 3.6"
    - "flightctl-python-client"
'''

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


class InventoryModule(BaseInventoryPlugin, Constructable):
    NAME = 'flightctl.core.flightctl'  # used internally by Ansible, must match the filename

    LIMIT_PER_PAGE: int = 1000

    def __init__(self, *args, **kwargs):
        super(InventoryModule, self).__init__(*args, **kwargs)
        self.config = None
        self._display = Display()

    def error(self, message):
        self._display.error(message)

    def info(self, message, min_verbosity_level: int = 0):
        if self._display.verbosity >= min_verbosity_level:
            msg = str(message)
            if min_verbosity_level >= 2:
                self._display.vvv(msg)
            elif min_verbosity_level == 1:
                self._display.vv(msg)
            else:
                self._display.v(msg)

    def verify_file(self, path: str) -> bool:
        """ Verify that the source file can be processed correctly. """
        if super(InventoryModule, self).verify_file(path):
            # Checking if file ends with 'inventory.yml' or 'inventory.yaml'
            valid_extensions = ('inventory.yml', 'inventory.yaml')
            return path.endswith(valid_extensions)
        self.error('Skipping due to inventory source suffix is neither "inventory.yaml" nor "inventory.yml"')
        return False

    def parse(self, inventory: Any, loader: Any, path: str, cache: bool = False) -> None:
        """
        Parse the inventory file.
        cache: we're not going to cache devices due to their highly volatile nature, hence False as a default value
        """
        if CLIENT_IMPORT_ERROR:
            raise CLIENT_IMPORT_ERROR

        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Load configuration parameters from the inventory file
        self._read_config_data(path)
        self.config = self._setup_connection_configuration()

        # Fetch devices and fleets
        devices, fleets = _get_devices_and_fleets(self.config, self.LIMIT_PER_PAGE)
        self.info(f"Retrieved {len(devices)} devices")
        self.info(f"Retrieved {len(fleets)} fleets")

        # Process devices, fleets and additional groups to inventory data
        self._populate_inventory_devices(devices)
        self._populate_inventory_fleets(fleets, self.config)
        self._populate_inventory_additional_groups(additional_groups=self.get_option('additional_groups'))

    def _load_config_file(self) -> ConfigLoader | None:
        """ Load configuration files using ConfigLoader. """
        # Only support flightctl_config_file
        config_file = None
        try:
            config_file = self.get_option("flightctl_config_file")
        except Exception:
            config_file = None
        if not config_file:
            return None

        try:
            # Use ConfigLoader to load config from file or fallback to defaults
            self.info(f"Loading configuration file {config_file}", min_verbosity_level=1)
            return ConfigLoader(config_file=config_file)
        except Exception as e:
            raise FlightctlException(f"Failed to load the config file: {e}") from e

    def _create_tmp_crt(self, encoded_data):
        decoded_data = base64.b64decode(encoded_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".crt") as temp_file:
            # Write our decoded data to a .crt file and point our ca_path to the filename
            temp_file.write(decoded_data)
            temp_file.flush()
            self.ca_path = temp_file.name
            self.info(f"crt file {temp_file.name} was created", min_verbosity_level=1)

            # Ensure the created temp file is deleted when our module exits
            self.add_cleanup_file(temp_file.name)

    def _setup_connection_configuration(self) -> Configuration:
        """
        Read Flight Control's config file if supplied.
        Override values with those supplied in an inventory setup
        """
        config_file: ConfigLoader = self._load_config_file()
        host = (self.get_option('host')
                or (getattr(config_file, 'host', None) if config_file else None))
        if not host:
            raise ValidationException("host is required in inventory mode")
        verify_ssl = self.get_option('verify_ssl')
        if verify_ssl is None:  # only when the user omitted the option
            verify_ssl = (getattr(config_file, 'verify_ssl', None)
                          or getattr(config_file, 'flightctl_verify_ssl', None))
        if verify_ssl is None:
            verify_ssl = False
        access_token = (self.get_option('token')
                        or (getattr(config_file, 'token', None) if config_file else None))
        username = (self.get_option('username')
                    or (getattr(config_file, 'username', None) if config_file else None))
        password = (self.get_option('password')
                    or (getattr(config_file, 'password', None) if config_file else None))
        if verify_ssl and not (access_token or (username and password)):
            raise ValidationException(
                "Authentication is required: provide either access_token or both username and password")

        ca_path = (self.get_option('ca_path')
                   or (getattr(config_file, 'ca_path', None) if config_file else None)
                   or (getattr(config_file, 'flightctl_ca_path', None) if config_file else None))
        # Special case - when we have loaded certificate authority data that needs to be written
        # to a file so our underlying requests library can use it
        if not ca_path and hasattr(config_file, "ca_data"):
            self._create_tmp_crt(getattr(config_file, "ca_data"))
            ca_path = self.ca_path

        request_timeout = self.get_option('request_timeout') or 120.0

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
            self.info(f"Retrieved {len(devices)} devices from fleet {fleet_id}")
            for device in devices:
                if hasattr(device, 'to_dict'):
                    device = device.to_dict()
                device_id, metadata = _validate_device(device)
                if device_id not in self.inventory.hosts:
                    self._populate_inventory_devices([device])
                self._add_to_group(fleet_id, device_id)

    def _populate_inventory_devices(self, devices: List[Any]) -> None:
        """
        Populate self.inventory with a list of devices.
        - devices: list of device instances
        """
        if len(devices) == 0:
            return

        # Process devices
        for device in [device.to_dict() for device in devices]:
            device_id, metadata = _validate_device(device)
            self.info(f"Populating inventory with device {device}", min_verbosity_level=1)

            # add host
            self.inventory.add_host(device_id)  # Add host to Ansible inventory

            # add host variables
            for key, value in device.items():
                if key != 'custom_vars':  # Handle custom vars separately
                    self.inventory.set_variable(device_id, key, value)

            # Add any custom variables
            if 'custom_vars' in device and isinstance(device['custom_vars'], dict):
                for var_name, var_value in device['custom_vars'].items():
                    self.inventory.set_variable(device_id, var_name, var_value)

            # Set ansible_host if netIpDefault is available
            net_ip_default = (
                device.get('status', {})
                .get('systemInfo', {})
                .get('netIpDefault')
            )
            if net_ip_default:
                self.inventory.set_variable(device_id, 'ansible_host', net_ip_default)

    def _populate_inventory_additional_groups(self, additional_groups: List[Dict[str, Any]]) -> None:
        """
        Given lists of additional_groups, populate self.inventory
        - additional_groups: list of dicts with keys 'name', 'label_selectors', 'field_selectors'
        """
        # handle additional groups
        additional_groups_info = _prepare_additional_groups_info(additional_groups)
        self.info(f"Additional groups info: {additional_groups_info}", min_verbosity_level=1)
        for group_name, selectors in additional_groups_info.items():
            label_selectors, field_selectors = selectors
            devices = _get_devices_by_labels_and_fields(self.config, label_selectors, field_selectors,
                                                        self.LIMIT_PER_PAGE)
            self.info(
                f"Retrieved {len(devices)} devices for group {group_name} by labels {label_selectors} and fields {field_selectors}")
            for device in [device.to_dict() for device in devices]:
                device_id, metadata = _validate_device(device)
                self._add_to_group(group_name, device_id)

    def _add_to_group(self, group_name: str, device_id: str):
        """ Add a host into the given group (creating it if necessary) """
        group_name = _sanitize_group_name(group_name)
        if group_name not in self.inventory.groups:
            self.inventory.add_group(group_name)
            self.info(f"Group {group_name} added to inventory", min_verbosity_level=1)
        self.inventory.add_child(group_name, device_id)
        self.info(f"Added device {device_id} to group {group_name}", min_verbosity_level=1)


# ---------------------- Custom context manager ------------------
@contextmanager
def flightctl_apis(config: Configuration) -> Generator[tuple[DeviceApi, FleetApi], Any, None]:
    """ Context manager yielding both API clients (device_api, fleet_api) """
    with ApiClient(configuration=config) as client:
        yield DeviceApi(client), FleetApi(client)


# ---------------------- Static methods --------------------------
def _get_data(
        list_func: Callable[..., Any],
        label_list: str | None = None,
        field_list: str | None = None,
        limit: int | None = 1000,
        headers: Dict[str, str] | None = None,
        request_timeout: float | None = None,
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
                limit=limit,
                _headers=headers,
                _request_timeout=request_timeout,
            )
        except Exception as e:
            raise FlightctlApiException(f"Error retrieving data from Flight Control API: {e}") from e
        records: Sequence[T] = response.items
        all_records.extend(records)
        metadata = response.to_dict().get('metadata', {})
        continue_token = metadata.get("continue", None)

        if not continue_token:
            break

    return all_records


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
        label_selectors: str = ",".join(lbl_sel)

        fld_sel = group_cfg.get("field_selectors", [])
        if not all(selector.startswith(supported_field_selectors) for selector in fld_sel):
            display.error(f"additional group {group_name} must contain only supported field_selectors, {fld_sel} found")
            continue
        # Join all field selectors into a comma-separated string
        field_selectors: str = ",".join(fld_sel)

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
    device_id = metadata.get('name', None) or (
        device.get('status', {})
        .get('systemInfo', {})
        .get('hostname')
    )
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


def _fetch_fleet_devices(fleet_id: str, config, limit_per_page: int) -> List[Any]:
    """ Retrieve devices belonging to a fleet """
    field_list = f"metadata.owner = Fleet/{fleet_id}"
    with flightctl_apis(config) as (device_api, fleet_api):
        bearer = getattr(config, 'access_token', None)
        headers = {'Authorization': f'Bearer {bearer}'} if bearer else None
        if headers is None:
            username = getattr(config, 'username', None)
            password = getattr(config, 'password', None)
            if username and password:
                basic_credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(basic_credentials.encode('utf-8')).decode('utf-8')
                headers = {'Authorization': f'Basic {encoded_credentials}'}
        devices = _get_data(
            device_api.list_devices,
            field_list=field_list,
            limit=limit_per_page,
            headers=headers,
            request_timeout=getattr(config, 'request_timeout', None)
        )
    return devices


def _get_devices_and_fleets(config, limit_per_page: int) -> Tuple[List[DeviceList], List[FleetList]]:
    """
    Fetch all devices and fleets from Flight Control.
    Group devices according to fleets and additional groups.
    Note: Device may present in many groups
    """
    with flightctl_apis(config) as (device_api, fleet_api):
        bearer = getattr(config, 'access_token', None)
        headers = {'Authorization': f'Bearer {bearer}'} if bearer else None
        if headers is None:
            username = getattr(config, 'username', None)
            password = getattr(config, 'password', None)
            if username and password:
                basic_credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(basic_credentials.encode('utf-8')).decode('utf-8')
                headers = {'Authorization': f'Basic {encoded_credentials}'}
        # We're **always** fetching a full list of devices and fleets
        all_devices = _get_data(
            device_api.list_devices,
            limit=limit_per_page,
            headers=headers,
            request_timeout=getattr(config, 'request_timeout', None)
        )
        all_fleets = _get_data(
            fleet_api.list_fleets,
            limit=limit_per_page,
            headers=headers,
            request_timeout=getattr(config, 'request_timeout', None)
        )

    return all_devices, all_fleets


def _get_devices_by_labels_and_fields(config, label_selectors: str | None, field_selectors: str | None,
                                      limit_per_page: int) -> List[DeviceList]:
    """ Fetch all devices from Flight Control than got these labels and fields """
    label_selectors = None if label_selectors == "" else label_selectors
    field_selectors = None if field_selectors == "" else field_selectors
    with flightctl_apis(config) as (device_api, fleet_api):
        bearer = getattr(config, 'access_token', None)
        headers = {'Authorization': f'Bearer {bearer}'} if bearer else None
        if headers is None:
            username = getattr(config, 'username', None)
            password = getattr(config, 'password', None)
            if username and password:
                basic_credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(basic_credentials.encode('utf-8')).decode('utf-8')
                headers = {'Authorization': f'Basic {encoded_credentials}'}
        devices = _get_data(
            device_api.list_devices,
            label_list=label_selectors,
            field_list=field_selectors,
            limit=limit_per_page,
            headers=headers,
            request_timeout=getattr(config, 'request_timeout', None)
        )

    return devices

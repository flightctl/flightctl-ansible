#!/usr/bin/env python3

from __future__ import (absolute_import, division, print_function, annotations)

__metaclass__ = type

import re

DOCUMENTATION = r'''---
    plugin: flightctl.core.flightctl
    version_added: "0.5.0"
    plugin_type: inventory
    short_description: Returns Ansible inventory from Flightctl.
    description:
        - Returns Ansible inventory from Flightctl.
        - Uses the same API as other modules in this collection.
        - The plugin uses collection's API.
        - Parameters: api_url, api_token and validate_certs
        - These parameters are required, so you have to supply them here, even blank.
        - You can reuse these parameters by supplying a flightctl_config_file. It will override current parameters
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices:
                - flightctl.core.flightctl
        api_url:
            description: URL of your device management app API
            type: str
            required: true
        api_token:
            description: Authentication token for your API
            type: str
            required: false
        validate_certs:
            description: Verify SSL certificate if using HTTPS
            type: bool
            default: true
        additional_groups:
            description: Additional groups to add all hosts to
            type: list
            default: []
        filters:
            description: Filters to apply when retrieving devices
            type: dict
            default: {}
'''

from ..module_utils.exceptions import ValidationException, FlightctlApiException

from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable

from ansible.utils.display import Display

from flightctl import ApiClient
from flightctl.api.device_api import DeviceApi
from flightctl.api.fleet_api import FleetApi
from flightctl.configuration import Configuration
from flightctl.models.device_list import DeviceList
from flightctl.models.fleet_list import FleetList

from collections.abc import Callable
from typing import Union, List


def _get_data(
        list_func: Callable[..., Union[DeviceList, FleetList]],
        label_selector: str | None = None,
        field_selector: str | None = None,
        limit: int | None = None
) -> List:
    all_records = []
    continue_token = None
    while True:
        try:
            # Call list_devices passing the continuation token and other parameters
            response = list_func(
                var_continue=continue_token,  # Pass the current continuation token, if any
                label_selector=label_selector,
                field_selector=field_selector,
                limit=limit
            )
        except Exception as e:
            raise FlightctlApiException(f"Error retrieving data from FlightCTL API: {e}") from e
        records = response.items
        all_records.extend(records)
        metadata = response.metadata.to_dict() if response.metadata else {}
        continue_token = metadata.get("continue")

        if not continue_token:
            break

    return all_records


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = 'flightctl'  # used internally by Ansible, must match the filename

    def __init__(self, *args, **kwargs):
        super(InventoryModule, self).__init__(*args, **kwargs)
        self._display = Display(verbosity=3)

    def verify_file(self, path):
        """Verify that the source file can be processed correctly."""
        if super(InventoryModule, self).verify_file(path):
            # Checking if file ends with 'inventory.yml' or 'inventory.yaml'
            valid_extensions = ('inventory.yml', 'inventory.yaml')
            return path.endswith(valid_extensions)
        return False

    def parse(self, inventory, loader, path, cache=True):
        """Parse the inventory file"""
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Load configuration parameters from the inventory file
        self._read_config_data(path)

        # Parameters for connection
        connection_params = {}
        for key in ['api_url', 'api_token', 'validate_certs']:
            connection_params[key] = self.get_option(key)

        # Get cache key
        cache_key = self.get_cache_key(path)

        # Check if cache is active and we have a valid cache entry
        if cache and cache_key in self._cache:
            self._populate_from_cache(self._cache[cache_key])
            return

        inventory_data = self._get_devices_and_fleets(connection_params)
        self._cache[cache_key] = inventory_data

    def _get_devices_and_fleets(self, connection_params):
        api_url = connection_params.get('api_url')
        if not api_url:
            raise ValidationException("api_url is required in inventory mode")
        config = Configuration(
            host=api_url,
            access_token=connection_params.get('api_token'),
        )
        if 'validate_certs' in connection_params:
            config.verify_ssl = connection_params.get('validate_certs')
        else:
            config.verify_ssl = True

        # TODO read them from somewhere
        label_selector = None
        field_selector = None
        limit = 1000

        api_client = ApiClient(configuration=config)

        api_instance = DeviceApi(api_client)
        all_devices = _get_data(api_instance.list_devices, label_selector, field_selector, limit)
        self._display.display(f"Retrieved total of {len(all_devices)} devices")

        api_instance = FleetApi(api_client)
        all_fleets = _get_data(api_instance.list_fleets, label_selector, field_selector, limit)
        self._display.display(f"Retrieved total of {len(all_fleets)} fleets")

        if len(all_devices) == 0:
            return {
                'hosts': {},
                'groups': {}
            }

        # Process inventory data
        return self._populate_inventory(all_devices, all_fleets,
                                        self.get_option('additional_groups'),
                                        self.get_option('filters'))

    def _populate_from_cache(self, inventory_data):
        """Populate inventory from cached data."""
        for hostname, host_vars in inventory_data.get('hosts', {}).items():
            self.inventory.add_host(hostname)
            for var_name, var_value in host_vars.items():
                self.inventory.set_variable(hostname, var_name, var_value)

        for group_name, group_data in inventory_data.get('groups', {}).items():
            self.inventory.add_group(group_name)
            for hostname in group_data.get('hosts', []):
                self.inventory.add_child(group_name, hostname)
            if "vars" in group_data:
                for k, v in group_data["vars"].items():
                    self.inventory.set_variable(group_name, k, v)

    def _populate_inventory(self, devices, fleets, additional_groups, filters):
        """Populate inventory with device data.

        Args:
            devices: List of devices
            fleets: List of fleets (can be empty)
            additional_groups: Additional groups to add hosts to
            filters: Condition to filter devices

        Returns:
            Dict containing inventory data for caching
        """

        # TODO: handle empty fleets

        # Device
        #   metadata.owner  - a name of a fleet unless null
        #   metadata.labels - otherwise have to match labels
        #
        # Fleet
        #   metadata.name                   - ???
        #   spec.selector.match_labels      - labels to match against device's labels
        #   spec.selector.match_expressions - ???

        # This dict will be used to populate cache
        inventory_data = {
            'hosts': {},  # A mapping of hostname → host‑vars dict, for exampls
            # hosts = {
            #   "device‑123": {
            #     "id": "device‑123",
            #     "device_type": "router",
            #     "management_ip": "10.0.0.5",
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

        # Build index: fleet_name -> selector labels dict
        fleets_info = []
        for f in fleets:
            f = f.to_dict()
            name = f['metadata']['name']
            sel = (
                      f.get('spec', {})
                      .get('selector', {})
                      .get('metadata', {})
                  ) or {}
            fleets_info.append({"name": name, "labels": sel})

        # Process devices
        for device in devices:
            device = device.to_dict()
            metadata = device['metadata'] if device['metadata'] else {}
            # Use device name as the Ansible inventory hostname
            device_id = metadata['name']
            if not device_id:
                continue

            # add host
            self.inventory.add_host(device_id)  # Add host to Ansible inventory
            inventory_data['hosts'][device_id] = device.copy()

            # add host variables
            for key, value in device.items():
                if key != 'custom_vars':  # Handle custom vars separately
                    self.inventory.set_variable(device_id, key, value)
                    inventory_data['hosts'][device_id][key] = value

            # Add any custom variables
            if 'custom_vars' in device and isinstance(device['custom_vars'], dict):
                for var_name, var_value in device['custom_vars'].items():
                    self.inventory.set_variable(device_id, var_name, var_value)
                    inventory_data['hosts'][device_id][var_name] = var_value

            # Set ansible_host if management_ip is available
            if device.get('management_ip'):
                self.inventory.set_variable(device_id, 'ansible_host', device['management_ip'])
                inventory_data['hosts'][device_id]['ansible_host'] = device['management_ip']

            # determine fleet group
            owner = metadata.get('owner', None)
            if owner:
                group_name = owner
            else:
                dev_labels = metadata['labels'] or {}
                group_name = None
                for fl in fleets_info:
                    # require all key/value pairs in fl["labels"] to appear in dev_labels
                    if all(dev_labels.get(k) == v for k, v in fl["labels"].items()):
                        group_name = fl['name']
                        break

            # add the fleet group (if we found one)
            if group_name:
                group_name = re.sub(r'[-.]', '_', group_name)
                group_name = re.sub(r'^.*/', '', group_name)
                if group_name not in self.inventory.groups:
                    self.inventory.add_group(group_name)
                    inventory_data['groups'][group_name] = {'hosts': []}
                self.inventory.add_child(group_name, device_id)
                inventory_data['groups'][group_name]['hosts'].append(device_id)

            # add to any additional groups
            for extra in additional_groups:
                if extra not in self.inventory.groups:
                    self.inventory.add_group(extra)
                    inventory_data['groups'][extra] = {'hosts': []}
                self.inventory.add_child(extra, device_id)
                inventory_data['groups'][extra]['hosts'].append(device_id)
        return inventory_data

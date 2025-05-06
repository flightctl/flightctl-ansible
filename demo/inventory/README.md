# Ansible Dynamic Inventory Plugin for Flight Control Service

The plugin enables users to manage and automate edge device configurations through Ansible by integrating with Flight Control Service that maintains the inventory of remote edge devices. This plugin operates as a native Ansible inventory source and allows dynamic discovery, grouping, and metadata extraction of edge devices.

## Installation
The plugin is part of the Ansible Collection for Flight Control Service and doesn't require any additional installation steps.

## Configuration
The plugin expects a configuration file. Its parameters are available using the following command:
```bash
ansible-doc -t inventory flightctl.core.flightctl
```

A special parameter `flightctl_config_file` may include a path to the collection's config file. host, username, password, token, ca_path and ca_data will be taken from there.

Note: Any parameters from `flightctl_config_file` may be overridden in a plugin's own configuration file.

This is an example of a configuration file:
```yaml
---
plugin: flightctl.core.flightctl
flightctl_validate_certs: False
verify_ssl: False
additional_groups:
  - name: group0
    label_selectors:
      - fleet: 'fleet-00'
    field_selectors:
      - metadata.name = 'device-03'
      - metadata.name in ['device-03', 'device-01']
  - name: group6
    fleet: fleet-06
request_timeout: 120
flightctl_config_file: <path>/.config/flightctl/client.yaml
```
## Usage
### Prepare example data
```bash
ansible-playbook demo/inventory/prepare-devices-and-fleets.yml --extra-vars "flightctl_config_file='~/.config/flightctl/client.yaml'"  --extra-vars "flightctl_validate_certs=False"
```

### Fetch inventory
#### Get a list of devices and groups
```bash
ansible-inventory -i ~/.config/flightctl/flightctl.inventory.yaml --list
```
#### Use a list of devices and groups in a playbook
```bash
ansible-playbook demo/inventory/fetch-inventory.yml -i ~/.config/flightctl/flightctl.inventory.yaml
```

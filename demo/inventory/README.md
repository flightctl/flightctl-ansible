# Ansible Dynamic Inventory Plugin for Flight Control Service

The plugin enables users to manage and automate edge device configurations through Ansible by integrating with Flight Control Service that maintains the inventory of remote edge devices. This plugin operates as a native Ansible inventory source and allows dynamic discovery, grouping, and metadata extraction of edge devices.

## Installation
The plugin is part of the Ansible Collection for Flight Control Service and doesn't require any additional installation steps.

## Configuration
You can configure the plugin via inventory values and/or a FlightCtl config file. Available options are documented with:
```bash
ansible-doc -t inventory flightctl.core.flightctl
```

A special parameter `flightctl_config_file` points to the FlightCtl config file (typically `~/.config/flightctl/client.yaml`). The plugin reads:

- `authentication.token`
- `service.server`
- `service.insecureSkipVerify`
- `service.certificate-authority-data` (optional, base64 PEM)

Note: Values in the plugin inventory file override those from `flightctl_config_file`.

Example FlightCtl config file:

```yaml
---
authentication:
  token: "<your-token>"
service:
  server: "https://<fqdn>:<port>"
  insecureSkipVerify: true
  # certificate-authority-data: "<base64-PEM>"
```

Example inventory without a config file:

```yaml
plugin: flightctl.core.flightctl
host: "https://<fqdn>:<port>"
token: "<token>"
verify_ssl: false                    # or true with ca_path
# ca_path: "/path/to/ca.crt"
additional_groups:
  - name: group0
    label_selectors:
      - fleet: 'fleet-00'
    field_selectors:
      - metadata.name = 'device-03'
      - metadata.name in ['device-03', 'device-01']
  - name: group6
    field_selectors:
        - metadata.owner = "Fleet/fleet-06"
request_timeout: 120
```

Example inventory using a config file:

```yaml
plugin: flightctl.core.flightctl
flightctl_config_file: "~/.config/flightctl/client.yaml"
additional_groups:
  - name: group0
    label_selectors:
      - fleet: 'fleet-00'
    field_selectors:
      - metadata.name = 'device-03'
      - metadata.name in ['device-03', 'device-01']
  - name: group6
    field_selectors:
        - metadata.owner = "Fleet/fleet-06"
request_timeout: 120
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

# Ansible Collection for Flight Control Service

This Ansible Collection includes Ansible content to help automate the management of Flight Control resources.

## Description

This collection enables organizations to automate time-consuming, error-prone tasks, enhancing efficiency and reducing manual effort. By leveraging it, teams can quickly adapt to shifting conditions across diverse IT environments, improving both operational agility and resilience. Its primary goal is to streamline mission-critical workflows for better overall performance.

More information about Flight Control can be found in the [main repo](https://github.com/flightctl/flightctl/).  The [user docs](https://github.com/flightctl/flightctl/blob/main/docs/user/README.md) in particular are helpful for understanding the concepts and capabilities of Flight Control.

## Requirements

### Ansible version compatibility

Tested with the Ansible Core >= 2.15.0 versions, and the current development version of Ansible.

### Python version compatibility

This collection requires Python 3.10 or greater.

<!--
## Installation

The `flightctl.edge` collection can be installed with the Ansible Galaxy command-line tool:

```shell
ansible-galaxy collection install flightctl.edge
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: flightctl.edge
```

Note that if you install any collections from Ansible Galaxy, they will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```shell
ansible-galaxy collection install flightctl.edge --upgrade
```

A specific version of the collection can be installed by using the `version` keyword in the `requirements.yml` file:

```yaml
---
collections:
  - name: flightctl.edge
    version: 1.0.0
```

or using the ansible-galaxy command as follows

```shell
ansible-galaxy collection install flightctl.edge:==1.0.0
```

The Python module dependencies are not installed by ansible-galaxy. They must be installed manually using pip:

```shell
pip install -r requirements.txt
```

Refer to the following for more details.
* [using Ansible collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

-->
## Use Cases

You can either call modules, rulebooks and playbooks by their Fully Qualified Collection Name (FQCN), such as ansible.eda.activation, or you can call modules by their short name if you list the flightctl.edge collection in the playbook's collections keyword:

```yaml
---
  - name: Create a new test device
    flightctl.edge.flightctl:
      kind: Device
      name: "test-ansible-device"
      api_version: v1alpha1

  - name: Create a new device
    flightctl.edge.flightctl:
      kind: Device
      name: "test-ansible-device-2"
      resource_definition: "{{ lookup('file', 'device.yml') | from_yaml }}"

  - name: Update new test device
    flightctl.edge.flightctl:
      kind: Device
      name: "test-ansible-device"
      api_version: v1alpha1
      resource_definition:
        apiVersion: v1alpha1
        kind: Device
        metadata:
          labels:
            fleet: default
            novalue: ""

  - name: Get information about a specific device
    flightctl.edge.flightctl_info:
      kind: Device
      name: "test-ansible-device"

  - name: Delete a test device
    flightctl.edge.flightctl:
      kind: Device
      name: "test-ansible-device"
      state: absent

  - name: Get all devices
    flightctl.edge.flightctl_info:
      kind: Device

  - name: Get all fleets
    flightctl.edge.flightctl_info:
      kind: Fleet

  - name: Update the resource definition for a fleet
    flightctl.edge.flightctl:
      kind: Fleet
      name: "asible-test-fleet"
      resource_definition:
        spec:
          os:
            image: quay.io/redhat/rhde:9.3
```

## Testing

There are unit, sanity, and integration tests configured to run for this repository.
Currently only sanity and unit tests are run in CI via gihub workflows.

### Unit Tests

Run locally via `make test-unit`

### Sanity Tests

Run locally via `make test-sanity`

### Integration Tests

Integration tests are dependent on:
- A flightctl instance the tests can hit
  - Locally the easiest way is to run `make deploy` from the main flightctl repository
- The flightctl_host var inside integration_config.yml set to the running flightctl api service

Run locally via `make test-integration`

## License Information

See [LICENSE](./LICENSE) to see the full text.

# Ansible Collection for Flight Control Service

This Ansible Collection includes Ansible content to help automate the management of Flight Control resources.

## Description

This collection enables organizations to automate time-consuming, error-prone tasks, enhancing efficiency and reducing manual effort. By leveraging it, teams can quickly adapt to shifting conditions across diverse IT environments, improving both operational agility and resilience. Its primary goal is to streamline mission-critical workflows for better overall performance.

## Requirements

### Ansible version compatibility

Tested with the Ansible Core >= 2.15.0 versions, and the current development version of Ansible.

### Python version compatibility

This collection requires Python 3.10 or greater.

### Ansible Automation Platform compatibility  
  
If used with Ansible Automation Platform (AAP), the minimum supported version is 2.5.20250326 or greater.  
  
### Flight Control Service compatibility  
  
Requires Flight Control version 0.7 or greater.

See the [Ansible Core Support Matrix](https://docs.ansible.com/ansible/latest/reference_appendices/release_and_maintenance.html#ansible-core-support-matrix) to see which ansible versions are compatible with python versions.


## Installation

The `flightctl.core` collection can be installed with the Ansible Galaxy command-line tool:

```shell
ansible-galaxy collection install flightctl.core
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: flightctl.core
```

Note that if you install any collections from Ansible Galaxy, they will not be upgraded automatically when you upgrade the Ansible package.
To upgrade the collection to the latest available version, run the following command:

```shell
ansible-galaxy collection install flightctl.core --upgrade
```

A specific version of the collection can be installed by using the `version` keyword in the `requirements.yml` file:

```yaml
---
collections:
  - name: flightctl.core
    version: 0.7.0
```

or using the ansible-galaxy command as follows

```shell
ansible-galaxy collection install flightctl.core:0.7.0
```

The Python module dependencies are not installed by ansible-galaxy. They must be installed manually using pip:

```shell
pip install -r requirements.txt
```

Refer to the following for more details.
* [using Ansible collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.


## Usage

You can either call modules, rulebooks and playbooks by their Fully Qualified Collection Name (FQCN), such as flightctl.core, or you can call modules by their short name if you list the flightctl.core collection in the playbook's collections keyword:

```yaml
---
  - name: Create a new test device
    flightctl.core.flightctl_resource:
      kind: Device
      name: "test-ansible-device"
      api_version: flightctl.io/v1alpha1

  - name: Create a new device
    flightctl.core.flightctl_resource:
      kind: Device
      name: "test-ansible-device-2"
      resource_definition: "{{ lookup('file', 'device.yml') | from_yaml }}"

  - name: Update new test device
    flightctl.core.flightctl_resource:
      kind: Device
      name: "test-ansible-device"
      api_version: flightctl.io/v1alpha1
      resource_definition:
        apiVersion: flightctl.io/v1alpha1
        kind: Device
        metadata:
          labels:
            fleet: default
            novalue: ""

  - name: Get information about a specific device
    flightctl.core.flightctl_resource_info:
      kind: Device
      name: "test-ansible-device"

  - name: Delete a test device
    flightctl.core.flightctl_resource:
      kind: Device
      name: "test-ansible-device"
      state: absent

  - name: Get all devices
    flightctl.core.flightctl_resource_info:
      kind: Device

  - name: Get all fleets
    flightctl.core.flightctl_resource_info:
      kind: Fleet

  - name: Update the resource definition for a fleet
    flightctl.core.flightctl_resource:
      kind: Fleet
      name: "ansible-test-fleet"
      resource_definition:
        spec:
          os:
            image: quay.io/redhat/rhde:9.3
```

## Testing

There are unit, sanity, and integration tests configured to run for this repository.  Tests are configured to run via github actions on pull requests and can also be run locally.

`ansible-test` is used to run each of the test types.  For `ansible-test` to properly work the collection must be present in the following directory structure on your local machine:

{...}/ansible_collections/flightctl/core/{code_from_this_repo}

### Unit Tests

Run locally via `make unit-test`

### Sanity Tests

Run locally via `make sanity-test`

### Integration Tests

Integration tests are dependent on:
- A flightctl instance the tests can hit
- The flightctl_host var inside integration_config.yml set to the running flightctl api service

The easiest way to run tests locally is to:
- Run `make deploy` from the main flightctl repository
- Run `make write-integration-config` from this repository to create the proper integration config from your running services
- Run locally via `make integration-test`

## Support

flightctl.core collection v0.7.1 is for [Technical Preview](https://access.redhat.com/support/offerings/techpreview). If you encounter issues or have questions, you can submit a support request through the following channels:
 - GitHub Issues: Report bugs, request features, or ask questions by opening an issue in the [GitHub repository](https://github.com/flightctl/flightctl-ansible/issues).

## Release notes

See the [changelog](https://github.com/flightctl/flightctl-ansible/blob/main/CHANGELOG.rst).

## Related Information

More information about Flight Control can be found in the [main repo](https://github.com/flightctl/flightctl). The [user docs](https://github.com/flightctl/flightctl/blob/main/docs/user/README.md) in particular are helpful for understanding the concepts and capabilities of Flight Control.

## License Information

See [LICENSE](./LICENSE) to see the full text.

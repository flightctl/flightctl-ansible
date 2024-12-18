# Ansible Collection for Flight Control Service

This Ansible Collection includes Ansible content to help automate the management of Flight Control resources.

## Description

This collection enables organizations to automate time-consuming, error-prone tasks, enhancing efficiency and reducing manual effort. By leveraging it, teams can quickly adapt to shifting conditions across diverse IT environments, improving both operational agility and resilience. Its primary goal is to streamline mission-critical workflows for better overall performance.

## Requirements

### Ansible version compatibility

Tested with the Ansible Core >= 2.15.0 versions, and the current development version of Ansible.

### Python version compatibility

This collection requires Python 3.10 or greater.

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
    version: 0.2.0
```

or using the ansible-galaxy command as follows

```shell
ansible-galaxy collection install flightctl.core:==0.1.0
```

The Python module dependencies are not installed by ansible-galaxy. They must be installed manually using pip:

```shell
pip install -r requirements.txt
```

Refer to the following for more details.
* [using Ansible collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Use Cases

You can either call modules, rulebooks and playbooks by their Fully Qualified Collection Name (FQCN), such as ansible.eda.activation, or you can call modules by their short name if you list the flightctl.core collection in the playbook's collections keyword:

```yaml
---
  - name: Create a new test device
    flightctl.core.flightctl:
      kind: Device
      name: "test-ansible-device"
      api_version: v1alpha1

  - name: Create a new device
    flightctl.core.flightctl:
      kind: Device
      name: "test-ansible-device-2"
      resource_definition: "{{ lookup('file', 'device.yml') | from_yaml }}"

  - name: Update new test device
    flightctl.core.flightctl:
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
    flightctl.core.flightctl_info:
      kind: Device
      name: "test-ansible-device"

  - name: Delete a test device
    flightctl.core.flightctl:
      kind: Device
      name: "test-ansible-device"
      state: absent

  - name: Get all devices
    flightctl.core.flightctl_info:
      kind: Device

  - name: Get all fleets
    flightctl.core.flightctl_info:
      kind: Fleet

  - name: Update the resource definition for a fleet
    flightctl.core.flightctl:
      kind: Fleet
      name: "asible-test-fleet"
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

Run locally via `make test-unit`

### Sanity Tests

Run locally via `make test-sanity`

### Integration Tests

Integration tests are dependent on:
- A flightctl instance the tests can hit
- The flightctl_host var inside integration_config.yml set to the running flightctl api service

The easiest way to run tests locally is to:
- Run `make deploy` from the main flightctl repository
- Run `make write-integration-config` from this repository to create the proper integration config from your running services
- Run locally via `make test-integration`

## Publishing New Versions

Currently the publishing to Ansible Galaxy is manual and requires the following steps:

1. Update the version in the following places:
    1. The `version` in `galaxy.yml`
    2. This README's version in the Installation section
2. Update the CHANGELOG:
    1. Make sure you have [`antsibull-changelog`](https://pypi.org/project/antsibull-changelog/) installed.
    2. Make sure there are fragments for all known changes in `changelogs/fragments`.
    3. Run `antsibull-changelog release`.
3. Ensre the colleciton tarball builds properly
    1. Run `ansible-galaxy collection build`
4. Commit the changes and create a PR with the changes. Ensure CI tests pass and merge to main.
5. Pull and checkout latest main
6. Use git to tag the release appropriately
    1. `git tag -n`    # see current tags and their comments
    2. `git tag -a NEW_VERSION -m "comment here"` # the comment can be, for example,  "flightctl.core: 1.0.0"
    3. `git push upstream NEW_VERSION`
7. Build and push the collection to Galaxy
    1. Run `ansible-galaxy collection build`
    2. Fetch or configure your [Galaxy Token](https://galaxy.ansible.com/ui/token/) if you have not done so already.
    3. Publish the collection `ansible-galaxy collection publish path/to/built/collection.tar.gz --token=your_token_here`
8. Verify the new version exists on the [Flightctl Galaxy page](https://galaxy.ansible.com/flightctl/core)
9. In GitHub add a new release for the

## Support

If you encounter issues or have questions, you can submit a support request through the following channels:
 - GitHub Issues: Report bugs, request features, or ask questions by opening an issue in the [GitHub repository](https://github.com/flightctl/flightctl-ansible/issues).

## Release notes

See the [changelog](https://github.com/flightctl/flightctl-ansible/blob/main/CHANGELOG.md).

## Related Information

More information about Flight Control can be found in the [main repo](https://github.com/flightctl/flightctl). The [user docs](https://github.com/flightctl/flightctl/blob/main/docs/user/README.md) in particular are helpful for understanding the concepts and capabilities of Flight Control.

## License Information

See [LICENSE](./LICENSE) to see the full text.

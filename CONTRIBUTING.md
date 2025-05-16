## Publishing New Versions

### Publishing to Ansible Galaxy

Currently, the publishing to Ansible Galaxy is manual and requires the following steps:

1. Check out a release branch
    1. `git checkout -b release-NEW_VERSION`
2. Update the version in the following places:
    1. The `version` in `galaxy.yml`
    2. This README's referenced versions in the Installation section
3. Update the CHANGELOG:
    1. Install [`antsibull-changelog`](https://pypi.org/project/antsibull-changelog)
    2. Verify fragments exist for all known changes in `changelogs/fragments`.  Info about creating changelog fragments can be found [here](https://docs.ansible.com/ansible/devel/community/development_process.html#creating-a-changelog-fragment)
    3. Run `antsibull-changelog release`.
4. Build the collection tarball:
    1. Run `ansible-galaxy collection build`
    2. Verify the tarball `flightctl-core-{some-version}.tar.gz` was created in the current directory without build errors
5. Install and verify the collection tarball locally
    1. Install the built collection via `ansible-galaxy collection install flightctl-core-{some-version}.tar.gz --force`
    2. Run a basic playbook to verify functionality (examples can be found in demo/README.md)
6. Commit the changes and create a PR with the changes. Ensure CI tests pass and merge to main.
7. Pull and checkout the latest code from the main branch.
8. Use git to tag the release appropriately:
    1. `git tag -n` # see current tags and their comments
    2. `git tag -a NEW_VERSION -m "comment here"` # the comment can be, for example,  "flightctl.core: 0.7.0"
    3. `git push origin NEW_VERSION`
9. Build and push the collection to Galaxy:
    1. Run `ansible-galaxy collection build`
    2. Fetch or configure your [Galaxy Token](https://galaxy.ansible.com/ui/token/) if you have not done so already.
    3. Publish the collection `ansible-galaxy collection publish path/to/built/collection.tar.gz --token=your_token_here`
10. Verify the new version exists on the [Flightctl Galaxy page](https://galaxy.ansible.com/flightctl/core).

### Publishing to Automation Hub

#### Build the downstream Collection

To create the downstream build for Automation Hub, use the provided `downstream.sh` script. Follow these steps:

1. Navigate to the `ci` directory where the `downstream.sh` script is located:
2. Run the downstream.sh script with the -b option to build the downstream release:
```shell
./downstream.sh -b
```
3. Verify the tarball `redhat-edge_manager-{some-version}.tar.gz` was created in the current directory without build errors


#### Using the Automation Hub User Interface

To upload your collection using the Automation Hub user interface:

1. Log in to the **Red Hat Ansible Automation Platform**.
2. Navigate to **Automation Hub > My Namespaces**.
3. Click a namespace.
4. Click **Upload collection**.
5. In the **New collection** modal, click **Select file**. Locate the `.tar.gz` file on your system.
6. Click **Upload**.

#### Using the `ansible-galaxy` Client

To upload a collection using the `ansible-galaxy` client, enter the following command:

```shell
ansible-galaxy collection publish path/to/redhat-edge_manager-{some-version}.tar.gz --api-key=SECRET
```
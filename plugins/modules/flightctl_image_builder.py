#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_image_builder
short_description: Manage Flight Control Image Builder resources
version_added: 1.5.0
author:
  - "Siddarth Royapally (@SiddarthR56)"
description:
  - Create, cancel, or delete ImageBuild and ImageExport resources on the Flight Control Image Builder service.
options:
  kind:
    description:
      - The type of Image Builder resource to manage.
    choices: ["ImageBuild", "ImageExport"]
    required: true
    type: str
  name:
    description:
      - The name of the resource.
      - Required when O(state=absent) or O(state=cancelled).
    type: str
  resource_definition:
    description:
      - A valid YAML/dict definition for the resource.
      - Required when O(state=present).
    type: raw
  state:
    description:
      - Desired state of the resource.
      - C(present) creates the resource.
      - C(absent) deletes the resource.
      - C(cancelled) cancels a running build or export.
    choices: ["present", "absent", "cancelled"]
    default: "present"
    type: str
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - "flightctl (git+https://github.com/flightctl/flightctl-python-client.git)"
"""

EXAMPLES = r"""
- name: Create an image build
  flightctl.core.flightctl_image_builder:
    kind: ImageBuild
    state: present
    resource_definition:
      apiVersion: imagebuilder.flightctl.io/v1alpha1
      kind: ImageBuild
      metadata:
        name: my-build
      spec:
        source:
          containerFile: "FROM quay.io/centos/centos:stream9"
        destination:
          image: "quay.io/myorg/myimage:latest"

- name: Cancel a running image build
  flightctl.core.flightctl_image_builder:
    kind: ImageBuild
    name: my-build
    state: cancelled

- name: Delete an image build
  flightctl.core.flightctl_image_builder:
    kind: ImageBuild
    name: my-build
    state: absent

- name: Create an image export
  flightctl.core.flightctl_image_builder:
    kind: ImageExport
    state: present
    resource_definition:
      apiVersion: imagebuilder.flightctl.io/v1alpha1
      kind: ImageExport
      metadata:
        name: my-export
      spec:
        sourceType: ImageBuild
        sourceName: my-build
        format: iso

- name: Cancel a running image export
  flightctl.core.flightctl_image_builder:
    kind: ImageExport
    name: my-export
    state: cancelled
"""

RETURN = r"""
result:
  description:
    - The resource object. Empty dict when deleted.
  returned: success
  type: dict
"""

from ..module_utils.imagebuilder_module import FlightctlImageBuilderModule
from ..module_utils.exceptions import FlightctlException

KIND_OPERATIONS = {
    "ImageBuild": {
        "create": "create_image_build",
        "get": "get_image_build",
        "delete": "delete_image_build",
        "cancel": "cancel_image_build",
    },
    "ImageExport": {
        "create": "create_image_export",
        "get": "get_image_export",
        "delete": "delete_image_export",
        "cancel": "cancel_image_export",
    },
}


def main():
    argument_spec = dict(
        kind=dict(type="str", required=True, choices=["ImageBuild", "ImageExport"]),
        name=dict(type="str"),
        resource_definition=dict(type="raw"),
        state=dict(type="str", default="present", choices=["present", "absent", "cancelled"]),
    )

    module = FlightctlImageBuilderModule(argument_spec=argument_spec)

    kind = module.params["kind"]
    name = module.params.get("name")
    state = module.params.get("state")
    definition = module.params.get("resource_definition")
    ops = KIND_OPERATIONS[kind]

    try:
        if state == "present":
            if not definition:
                module.fail_json(msg="resource_definition is required when state=present")

            if module.check_mode:
                module.exit_json(changed=True)

            result = getattr(module, ops["create"])(definition)
            module.exit_json(changed=True, result=result.to_dict())

        elif state == "absent":
            if not name:
                module.fail_json(msg="name is required when state=absent")

            existing = getattr(module, ops["get"])(name)
            if not existing:
                module.exit_json(changed=False, result={})

            if module.check_mode:
                module.exit_json(changed=True)

            getattr(module, ops["delete"])(name)
            module.exit_json(changed=True, result={})

        elif state == "cancelled":
            if not name:
                module.fail_json(msg="name is required when state=cancelled")

            if module.check_mode:
                module.exit_json(changed=True)

            result = getattr(module, ops["cancel"])(name)
            module.exit_json(changed=True, result=result.to_dict())

    except FlightctlException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()

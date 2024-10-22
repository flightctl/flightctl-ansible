#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl
short_description: Describe Flight Control Resources
author:
  - "Alina Buzachis (@alinabuzachis)"
description:
  - Describe Flight Control Resources.
options:
  api_version:
    description:
      - Use to specify the API version.
      - Use to create, delete, or discover an object without providing a full resource definition.
      - If O(resource_definition) is provided, the C(apiVersion) value from the O(resource_definition)
        will override this option.
    type: str
    default: v1alpha1
  kind:
    description:
      - Use to specify an object model.
      - Use to create, delete, or discover an object without providing a full resource definition.
      - If O(resource_definition) is provided, the C(kind) value from the O(resource_definition)
        will override this option.
    type: str
  name:
    description:
      - Use to specify an object name.
      - Use to create, delete, or discover an object without providing a full resource definition.
      - If O(resource_definition) is provided, the C(metadata.name) value from the O(resource_definition)
        will override this option.
    type: str
  resource_definition:
    description:
      - Provide a valid YAML template definition file for an object when creating or updating.
      - Value can be provided as string or dictionary.
    type: raw
extends_documentation_fragment:
  - flightctl.edge.auth
  - flightctl.edge.state
notes:
  - For resources other than O(kind=Device), O(resource_definition) must be specified when creating or
    updating a resource.
requirements:
  - jsonschema
  - PyYAML
"""

EXAMPLES = r"""
- name: Create a device
  flightctl.edge.flightctl:
    kind: Device
    name: "Example"
    api_version: v1alpha1

- name: Create a device
  flightctl.edge.flightctl:
    kind: Device
    resource_definition:
      apiVersion: v1alpha1
      kind: Device
      metadata:
        name: "Example"
        labels:
          fleet: default
          novalue: ""

- name: Delete a device
  flightctl.edge.flightctl:
    kind: Device
    name: "Example"
"""

RETURN = r"""
result:
  description:
    - The created, patched, or otherwise present object. Will be empty in the case of a deletion.
  returned: success
  type: complex
  contains:
    apiVersion:
      description: The versioned schema of this representation of an object.
      returned: success
      type: str
    kind:
      description: Object model.
      returned: success
      type: str
    metadata:
      description: Object metadata.
      returned: success
      type: dict
    spec:
      description: Specific attributes of the object.
      returned: success
      type: dict
    status:
      description: Current status details for the object.
      returned: success
      type: dict
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.args_common import STATE_ARG_SPEC
from ..module_utils.exceptions import FlightctlException
from ..module_utils.runner import run_module


def main():
    argument_spec = dict(
        kind=dict(type="str"),
        name=dict(type="str"),
        api_version=dict(type="str", default="v1alpha1"),
        resource_definition=dict(type="raw"),
        **STATE_ARG_SPEC
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    try:
        run_module(module)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to run module: {e}")


if __name__ == "__main__":
    main()

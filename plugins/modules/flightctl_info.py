#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_info
short_description: Get information about Flight Control resources
author:
  - "Alina Buzachis (@alinabuzachis)"
description:
  - Get information about Flight Control resources.
options:
  kind:
    description:
      - Use to specify an object model.
    type: str
    required: True
  name:
    description:
      - Use to specify an object name.
    type: str
  fleet_name:
    description:
      - Use to specify a fleet name for accessing templateversions (Only applicable when kind is TemplateVersions).
    type: str
  label_selector:
    description:
      - A selector to restrict the list of returned objects by their labels.
    type: str
  owner:
    description:
      - Filter results by owner, specified in kind/name format.
  rendered:
    description:
      - Return the rendered device configuration that is presented to the device (Only applicable when kind is Device).
    type: bool
    default: False
extends_documentation_fragment:
  - flightctl.edge.auth
requirements:
  - jsonschema
  - PyYAML
"""


EXAMPLES = r"""
- name: Get all devices
  flightctl.edge.flightctl_info:
    kind: Device

- name: Get all fleets
  flightctl.edge.flightctl_info:
    kind: Fleet

- name: Get information about a specific device
  flightctl.edge.flightctl_info:
    kind: Device
    name: "Example"

- name: Get information about a specific device using label_selector
  flightctl.edge.flightctl_info:
    kind: Device
    label_selector: "owner=test"

- name: Get all template versions for a specific fleet
  flightctl.edge.flightctl_info:
    kind: TemplateVersion
    fleet_name: test_fleet
"""


RETURN = r"""
result:
  description:
    - The object(s) that exists
  returned: success
  type: list
  elements: dict
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
from ..module_utils.exceptions import FlightctlException, ValidationException
from ..module_utils.inputs import InfoInput
from ..module_utils.constants import Kind


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        kind=dict(required=True),
        name=dict(type="str"),
        label_selector=dict(type="str"),
        fleet_name=dict(type="str"),
        owner=dict(type="str"),
        rendered=dict(type=bool),
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    # TODO move this to a perform function instead?
    try:
        kind = Kind(module.params.get("kind"))
    except (TypeError, ValueError):
        raise ValidationException(f"Invalid Kind {module.params.get('kind')}")

    input = InfoInput(
        kind=kind,
        name=module.params.get("name"),
        label_selector=module.params.get("label_selector"),
        fleet_name=module.params.get("fleet_name"),
        owner=module.params.get("owner"),
        rendered=module.params.get("rendered")
    )

    # Attempt to look up resource based on the provided name
    try:
        result = module.get_one_or_many(
          input.kind.value,
          name=input.name,
          fleet_name=input.fleet_name,
          **input.to_request_params()
        )
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to get resource: {e}")

    module.exit_json(result=result)


if __name__ == "__main__":
    main()

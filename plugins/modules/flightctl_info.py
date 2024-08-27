#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


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
  label_selector:
    description:
      - A selector to restrict the list of returned objects by their labels.
    type: str
extends_documentation_fragment:
  - flightctl.edge.auth
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
      type: complex
    spec:
      description: Specific attributes of the object.
      returned: success
      type: complex
    status:
      description: Current status details for the object.
      returned: success
      type: complex
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        kind=dict(required=True),
        name=dict(type="str"),
        label_selector=dict(type="str"),
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    name = module.params.get("name")
    kind = module.params.get("kind")

    params = {}
    if module.params.get("label_selector"):
        params["labelSelector"] = module.params["label_selector"]

    # Attempt to look up resource based on the provided name
    try:
        result = module.get_one_or_many(kind, name=name, **params)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to get resource: {e}")

    module.exit_json(result=result)


if __name__ == "__main__":
    main()

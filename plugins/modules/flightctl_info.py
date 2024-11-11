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
      - Use to specify a fleet name that owns the associated resources. Only applicable when kind is TemplateVersions.
    type: str
  label_selector:
    description:
      - A selector to restrict the list of returned objects by their labels.  Accepts a a comma-separated list of key1=value1,key2=value2
    type: str
  field_selector:
    description:
      - A selector to filter based on object fields.  Accepts a a comma-separated list of key1=value1,key2=value2
    type: str
  owner:
    description:
      - Filter results by owner, specified in kind/name format.
    type: str
  rendered:
    description:
      - Return the rendered device configuration that is presented to the device.  Only applicable when kind is Device.
    type: bool
  summary:
    description:
      - Return aggregate summary info for devices within a fleet.  Only applicable when kind is Fleet.
    type: bool
  summary_only:
    description:
      - Return only the summary info for devices.  Only the 'owner' and 'label_selector' parameters are supported. Only applicable when kind is Device.
    type: bool
  status_filter:
    description:
      - A filter to restrict the list of devices by the value of the filtered status key.  Only applicable when kind is Device.
    type: list
    elements: str
    default: []
  limit:
    description:
      - Maximum number of resources returned.  Only applicable when querying lists of resources.
    type: int
  continue_token:
    description:
      - Use to retrieve the next set of available objects.
    type: str
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
    label_selector: "machine_type=forklift"

- name: Get devices with a specific owner
    flightctl.edge.flightctl_info:
      kind: Device
      owner: "Fleet/{{ fleet_name }}"

- name: Get devices filtered by status
    flightctl.edge.flightctl_info:
      kind: Device
      status_filter: ['updated.status=OutOfDate']

- name: Get devices filtered by a field selector
    flightctl.edge.flightctl_info:
      kind: Device
      field_selector: "metadata.name!={{ deivce_name }}"

- name: Get all template versions for a specific fleet
  flightctl.edge.flightctl_info:
    kind: TemplateVersion
    fleet_name: test_fleet
"""


RETURN = r"""
result:
  description:
    - The list response containing the object(s) that exist and relevant metadata
  returned: sucess
  type: complex
  contains:
    data:
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
    metadata:
      description:
        - Request metadata for requesting additional resources from list endpoints.
      type: dict
      returned: When C(name) is not used and a list of objects is fetched
      contains:
        continue_token:
          description: An opaque token used to issue another request to the endpoint that served a list to retrieve the next set of available objects.
          returned: When the total number of items queried is greater than C(limit) or the default limit.
          type: str
        remainingItemCount:
          description: The number of subsequent items in the list which are not included in this list response.
          returned: When the total number of items queried is greater than C(limit) or the default limit.
          type: int
    summary:
      description:
        - A summary rollup of queried objects
      returned: When C(summary_only) is true
      type: dict
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException, ValidationException
from ..module_utils.options import GetOptions
from ..module_utils.constants import Kind


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        kind=dict(required=True),
        name=dict(type="str"),
        label_selector=dict(type="str"),
        field_selector=dict(type="str"),
        fleet_name=dict(type="str"),
        owner=dict(type="str"),
        rendered=dict(type="bool"),
        summary=dict(type="bool"),
        summary_only=dict(type="bool"),
        status_filter=dict(type="list", elements="str", default=[]),
        limit=dict(type="int"),
        continue_token=dict(type="str", no_log=True)
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    try:
        kind = Kind(module.params.get("kind"))
    except (TypeError, ValueError):
        raise ValidationException(f"Invalid Kind {module.params.get('kind')}")

    options = GetOptions(
        kind=kind,
        name=module.params.get("name"),
        label_selector=module.params.get("label_selector"),
        field_selector=module.params.get("field_selector"),
        fleet_name=module.params.get("fleet_name"),
        owner=module.params.get("owner"),
        rendered=module.params.get("rendered"),
        summary=module.params.get("summary"),
        summary_only=module.params.get("summary_only"),
        status_filter=module.params.get("status_filter"),
        limit=module.params.get("limit"),
        continue_token=module.params.get("continue_token")
    )

    # Attempt to look up resource based on the provided name
    try:
        result = module.get_one_or_many(options)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to get resource: {e}")

    module.exit_json(result=result.dict)


if __name__ == "__main__":
    main()

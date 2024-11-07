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
      - Use to specify a fleet name for accessing templateversions. Only applicable when kind is TemplateVersions.
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
      - Return the rendered device configuration that is presented to the device.  Only applicable when kind is Device.
    type: bool
    default: False
  summary:
    description:
      - Return aggregate summary info for devices within a fleet.  Only applicable when kind is Fleet.
    type: bool
  summary_only:
    description:
      - Return only the summary info for devices.  Only the 'owner' and 'label_selector' parameters are supported. Only applicable when kind is Device.
    type: bool
    default: False
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
    label_selector: "owner=test"

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
    items:
      description:
        - The object(s) that exists
      returned: success
      type: list
      elements: complex
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
      - Request metadata for requesting additional resources form list endpoints.
    type: dict
    returned: when C(name) is not used and a list of objects is fetched
    contains:
      continue_token:
        description: An opaque token used to issue another request to the endpoint that served a list to retrieve the next set of available objects.
        returned: when C(limit) is used and less values than the limit are returned, or when the number of items returned is greater than the server default limit.
      remainingItemCount:
        description: The number of subsequent items in the list which are not included in this list response.
        returned: when C(limit) is used and less values than the limit are returned, or when the number of items returned is greater than the server default limit.
  summary:
    description:
      - A summary rollup of queried objects
    returned: when C(summary_only) is true
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
        summary=dict(type=bool),
        summary_only=dict(type=bool),
        limit=(dict(type=int)),
        continue_token=(dict(type=str))
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    # TODO move this to a perform function instead?
    try:
        kind = Kind(module.params.get("kind"))
    except (TypeError, ValueError):
        raise ValidationException(f"Invalid Kind {module.params.get('kind')}")

    # TODO use an argument spec validator instead of validation in the input? https://docs.ansible.com/ansible/latest/reference_appendices/module_utils.html#argumentspecvalidator
    input = InfoInput(
        kind=kind,
        name=module.params.get("name"),
        label_selector=module.params.get("label_selector"),
        fleet_name=module.params.get("fleet_name"),
        owner=module.params.get("owner"),
        rendered=module.params.get("rendered"),
        summary=module.params.get("summary"),
        summary_only=module.params.get("summary_only"),
        limit=module.params.get("limit"),
        continue_token=module.params.get("continue_token")
    )

    # Attempt to look up resource based on the provided name
    try:
        result = module.get_one_or_many(
          input.kind.value,
          name=input.name,
          fleet_name=input.fleet_name,
          rendered=input.rendered,
          **input.to_request_params()
        )
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to get resource: {e}")

    # TODO figure out how the output is seen by ansible to avoid stuff like
    # device_with_owner_result.result["items"][0].metadata.name == "ansible-integration-test-device"
    # where sometimes dot notation works and sometimes it doesn't and its unclear why
    # maybe something to do with dataclass internals?
    module.exit_json(result=result.dict)


if __name__ == "__main__":
    main()

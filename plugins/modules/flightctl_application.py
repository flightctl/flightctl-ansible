#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_application
short_description: Start, stop, or restart Flight Control applications
version_added: 1.7.0
author:
  - "Efrat Ifergan (@EfratIfergan)"
description:
  - Start, stop, or restart an application on a Flight Control Device or Fleet.
options:
  kind:
    description:
      - The target resource type.
    choices: ["Device", "Fleet"]
    required: true
    type: str
  name:
    description:
      - The name of the Device or Fleet that contains the application.
    required: true
    type: str
  app_name:
    description:
      - The name of the application to control.
    required: true
    type: str
  state:
    description:
      - The requested application lifecycle action.
      - C(restarted) is supported only when O(kind=Device).
    choices: ["started", "stopped", "restarted"]
    required: true
    type: str
attributes:
  check_mode:
    description: Supports check mode.
    support: full
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - flightctl-client
"""


EXAMPLES = r"""
- name: Start an application on a device
  flightctl.core.flightctl_application:
    kind: Device
    name: edge-1
    app_name: workload
    state: started

- name: Stop an application on a fleet
  flightctl.core.flightctl_application:
    kind: Fleet
    name: production
    app_name: workload
    state: stopped

- name: Restart an application on a device
  flightctl.core.flightctl_application:
    kind: Device
    name: edge-1
    app_name: workload
    state: restarted
"""


RETURN = r"""
result:
  description:
    - The updated Device or Fleet resource.
  returned: success
  type: dict
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException
from ..module_utils.runner import perform_application_action


def main():
    argument_spec = dict(
        kind=dict(type="str", required=True, choices=["Device", "Fleet"]),
        name=dict(type="str", required=True),
        app_name=dict(type="str", required=True),
        state=dict(type="str", required=True, choices=["started", "stopped", "restarted"]),
    )
    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )
    try:
        perform_application_action(module)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed application action: {e}")


if __name__ == "__main__":
    main()

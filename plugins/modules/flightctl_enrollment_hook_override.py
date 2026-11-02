#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_enrollment_hook_override
short_description: Override a failed device enrollment hook
version_added: 1.8.0
author:
  - "Flight Control contributors"
description:
  - Manually override a failed enrollment hook condition for a device.
  - This is an action and does not create or update an Ansible resource.
options:
  name:
    description:
      - The name of the device whose failed enrollment hook should be overridden.
    type: str
    required: true
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - flightctl-client
"""

EXAMPLES = r"""
- name: Override a failed enrollment hook
  flightctl.core.flightctl_enrollment_hook_override:
    name: device-01
"""

RETURN = r"""
result:
  description:
    - The device returned by the enrollment-hook override action.
  returned: success
  type: dict
"""

from flightctl.api.device_api import DeviceApi
from flightctl.exceptions import ApiException

from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException
from ..module_utils.sdk_utils import raw_response_to_dict


def main():
    module = FlightctlAPIModule(
        argument_spec=dict(
            name=dict(type="str", required=True),
        )
    )

    name = module.params.get("name")
    if not name:
        module.fail_json(msg="name is required")

    if module.check_mode:
        module.exit_json(changed=True)

    try:
        api = DeviceApi(module.client)
        # This mutating endpoint is intentionally called through its raw
        # response variant.  Deserializing the response with the generated
        # client can fail after the server has already applied the override;
        # using the raw response avoids an unsafe retry of the action.
        response = module.call_api(
            api.override_device_enrollment_hook_without_preload_content,
            name,
        )
        result = raw_response_to_dict(response)
        module.exit_json(changed=True, result=result)
    except (ApiException, FlightctlException, ValueError) as exc:
        module.fail_json(msg=f"Failed to override enrollment hook: {exc}")


if __name__ == "__main__":
    main()

#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_enrollment_config_info
short_description: Get information about enrollment configuration.
version_added: 1.0.0
author:
  - "Dakota Crowder (@dakcrowder)"
description:
  - Get information about enrollment configuration.
  - Configuration is only returned for approved certificate signing requests.
options:
  name:
    description:
      - Use to specify the name of an approved certificate signing request.
    type: str
    required: True
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - jsonschema
  - PyYAML
  - "flightctl (git+https://github.com/flightctl/flightctl-python-client.git)"
"""


EXAMPLES = r"""
- name: Get enrollment config for an approved csr
  flightctl.core.flightctl_enrollment_config_info:
    name: some-csr-name
"""


RETURN = r"""
result:
  description:
    - The enrollment config
  returned: success
  type: dict
  contains:
    enrollment_service:
      description: Contains enrollment service data.
      returned: success
      type: dict
      contains:
        authentication:
          description: Contains authentication details for an agent to use when enrolling a device.
          type: dict
          returned: success
          contains:
            client_certificate_data:
              description: Client certificate data.
              type: str
              returned: success
            client_key_data:
              description: Client key data.
              type: str
              returned: success
        service:
          description: Service-related information an agent will use after enrollment is complete.
          type: dict
          returned: success
          contains:
            certificate_authority_data:
              description: Certificate authority data.
              type: str
              returned: success
            server:
              description: Server address.
              type: str
              returned: success
        enrollment_ui_endpoint:
          description: Enrollment ui endpoint.
          type: str
          returned: success
    grpc_management_endpoint:
      description: grpc management endpoint.
      returned: success
      type: str
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.constants import ResourceType
from ..module_utils.exceptions import FlightctlException
from ..module_utils.options import GetOptions


def main():
    argument_spec = dict(
        name=dict(type="str", required=True),
    )

    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    resource = ResourceType.ENROLLMENT_CONFIG
    options = GetOptions(
        resource=resource,
        name=module.params.get("name")
    )

    try:
        result = module.get(options)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to get resource: {e}")

    module.exit_json(result=result.to_dict())


if __name__ == "__main__":
    main()

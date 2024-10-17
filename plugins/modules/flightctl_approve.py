#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


DOCUMENTATION = r"""
module: flightctl_approve
short_description: Approve or deny enrollment requests
author:
  - "Dakota Crowder (@dakcrowder)"
description:
  - Approve or deny enrollment requests
options:
  name:
    description:
      - Use to specify a device name
    type: str
  approved:
    description:
      - Indicates if the request should be approved (if True) or denied (if False)
    type: bool
    required: True
  approvedBy:
    description:
      - Name of the approver
    type: str
  labels:
    description:
      - Labels that will be applied to the device on approval
    type: dict
extends_documentation_fragment:
  - flightctl.edge.auth
"""


EXAMPLES = r"""
- name: Approve an enrollment request
  flightctl.edge.flightctl_approve:
    approved: True
    approvedBy: ExampleUser
    labels:
      some_label: label_value

- name: Deny an enrollment request
  flightctl.edge.flightctl_approve:
    approved: False
    approvedBy: ExampleUser
    labels:
      some_label: label_value
"""


RETURN = r"""
result:
  description:
    - The result of the approval request
  returned: success
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException


def main():
    # TODO: Generalize this module to also allow for apprving csr requests
    kind = "EnrollmentRequest"
    
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        name=dict(type="str"),
        approved=dict(type="bool", required=True),
        approvedBy=dict(type="str"),
        labels=dict(type="dict"),
    )
    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )

    name = module.params.get("name")
    params = {}
    if module.params.get("approved"):
        params["approved"] = module.params["approved"]
    if module.params.get("approvedBy"):
        params["approvedBy"] = module.params["approvedBy"]
    if module.params.get("labels"):
        params["labels"] = module.params["labels"]

    # Attempt to approve the enrollment request identified by name
    try:
        result = module.approve(kind, name=name, **params)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed to approve enrollmentrequest: {e}")

    module.exit_json(result=result)


if __name__ == "__main__":
    main()

#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_certificate
short_description: Approve or deny certificate signing or enrollment requests.
author:
  - "Dakota Crowder (@dakcrowder)"
description:
  - Approve or deny certificate signing or enrollment requests.
options:
  kind:
    description:
      - Use to specify an object model.
    type: str
    required: True
  name:
    description:
      - Use to specify a name corresponding to the resource kind.
    type: str
  approved:
    description:
      - Indicates if the request should be approved (if True) or denied (if False).
    type: bool
    required: True
  approved_by:
    description:
      - Name of the approver.
    type: str
  labels:
    description:
      - Labels that will be applied on approval.
    type: dict
extends_documentation_fragment:
  - flightctl.edge.auth
"""


EXAMPLES = r"""
- name: Approve an enrollment request
  flightctl.edge.flightctl_certificate:
    kind: EnrollmentRequest
    approved: True
    approved_by: ExampleUser
    labels:
      some_label: label_value

- name: Deny an enrollment request
  flightctl.edge.flightctl_certificate:
    kind: EnrollmentRequest
    approved: False
    approved_by: ExampleUser
    labels:
      some_label: label_value

- name: Approve a certificate signing request
  flightctl.edge.flightctl_certificate:
    kind: CertificateSigningRequest
    approved: True
    labels:
      some_label: label_value
"""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException
from ..module_utils.runner import perform_approval


def main():
    # Any additional arguments that are not fields of the item can be added here
    argument_spec = dict(
        kind=dict(required=True),
        name=dict(type="str"),
        approved=dict(type="bool", required=True),
        approved_by=dict(type="str"),
        labels=dict(type="dict"),
    )
    module = FlightctlAPIModule(
        argument_spec=argument_spec,
    )
    try:
        perform_approval(module)
    except FlightctlException as e:
        module.fail_json(msg=f"Failed certificate action: {e}")


if __name__ == "__main__":
    main()

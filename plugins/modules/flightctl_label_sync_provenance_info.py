#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_label_sync_provenance_info
short_description: Query LabelSyncMapping ownership for label keys
version_added: 1.8.0
author:
  - "Flight Control contributors (@flightctl)"
description:
  - Query the current LabelSyncMapping owners for a device or exact label keys.
  - This is a read-only query and does not create or update an Ansible resource.
options:
  name:
    description:
      - The name of the device whose currently owned label keys should be queried.
    type: str
  label_keys:
    description:
      - Exact label keys to resolve at the organization level.
      - The API accepts between 1 and 50 keys and preserves request order and duplicates.
    type: list
    elements: str
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - flightctl-client
"""

EXAMPLES = r"""
- name: Get label-sync provenance for a device
  flightctl.core.flightctl_label_sync_provenance_info:
    name: device-01

- name: Resolve exact label keys in an organization
  flightctl.core.flightctl_label_sync_provenance_info:
    label_keys:
      - example.com/site
      - example.com/tier
      - example.com/site
"""

RETURN = r"""
result:
  description:
    - Label-sync provenance items, including each exact key and its current owners.
  returned: success
  type: dict
  contains:
    items:
      description:
        - One item per owned device key or per supplied organization key.
      type: list
      elements: dict
      contains:
        key:
          description: Exact label key.
          type: str
        owners:
          description: Current owning LabelSyncMapping resource names.
          type: list
          elements: str
"""

try:
    from flightctl.api.device_api import DeviceApi
    from flightctl.api.labelsyncmapping_api import LabelsyncmappingApi
    from flightctl.exceptions import ApiException
except ImportError:  # The client is an optional runtime dependency.
    DeviceApi = None
    LabelsyncmappingApi = None

    class ApiException(Exception):
        """Placeholder when the optional client dependency is unavailable."""


from ..module_utils.api_module import FlightctlAPIModule
from ..module_utils.exceptions import FlightctlException
from ..module_utils.sdk_utils import is_pydantic_validation_error, raw_response_to_dict


def _get_query(module):
    name = module.params.get("name")
    label_keys = module.params.get("label_keys")

    if name is not None and label_keys is not None:
        module.fail_json(msg="name and label_keys are mutually exclusive")

    if name is not None:
        if not name:
            module.fail_json(msg="name must not be empty")
        return name, None

    if label_keys is None:
        module.fail_json(msg="exactly one of name or label_keys is required")

    if not isinstance(label_keys, list) or not 1 <= len(label_keys) <= 50:
        module.fail_json(msg="label_keys must contain between 1 and 50 keys")

    if any(not isinstance(key, str) or not key for key in label_keys):
        module.fail_json(msg="label_keys must contain only non-empty strings")

    return None, label_keys


def _query(module, api, method, raw_method, *args):
    try:
        response = module.call_api(method, *args)
    except Exception as exc:
        if not is_pydantic_validation_error(exc):
            raise
        response = raw_response_to_dict(module.call_api(raw_method, *args))

    return response.to_dict() if hasattr(response, "to_dict") else response


def main():
    module = FlightctlAPIModule(
        argument_spec=dict(
            name=dict(type="str"),
            label_keys=dict(type="list", elements="str", no_log=True),
        )
    )

    name, label_keys = _get_query(module)

    try:
        if name is not None:
            api = DeviceApi(module.client)
            result = _query(
                module,
                api,
                api.get_device_label_sync_provenance,
                api.get_device_label_sync_provenance_without_preload_content,
                name,
            )
        else:
            api = LabelsyncmappingApi(module.client)
            result = _query(
                module,
                api,
                api.get_label_sync_provenance,
                api.get_label_sync_provenance_without_preload_content,
                label_keys,
            )

        # Keep the API's item ordering and duplicate-key semantics unchanged.
        module.exit_json(result=result)
    except (ApiException, FlightctlException, ValueError) as exc:
        module.fail_json(msg=f"Failed to get label-sync provenance: {exc}")


if __name__ == "__main__":
    main()

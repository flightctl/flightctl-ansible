#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = r"""
module: flightctl_image_builder_info
short_description: Get information about Flight Control Image Builder resources
version_added: 1.5.0
author:
  - "Siddarth Royapally (@SiddarthR56)"
description:
  - Retrieve information about ImageBuild and ImageExport resources from the Flight Control Image Builder service.
  - Can fetch a single resource by name, list resources with filters, retrieve logs, or download an exported artifact.
options:
  kind:
    description:
      - The type of Image Builder resource to query.
    choices: ["ImageBuild", "ImageExport"]
    required: true
    type: str
  name:
    description:
      - The name of a specific resource to retrieve.
      - When omitted, lists all resources of the given O(kind) (subject to filters).
    type: str
  log:
    description:
      - If C(true), return the build/export log instead of the resource definition.
      - Only valid when O(name) is specified.
    type: bool
    default: false
  download:
    description:
      - If C(true), download the exported image artifact.
      - Only valid when O(kind=ImageExport) and O(name) is specified.
      - The artifact is returned as base64-encoded content in the result.
    type: bool
    default: false
  with_exports:
    description:
      - If C(true), include related ImageExport resources in the response.
      - Only applicable when O(kind=ImageBuild).
    type: bool
  label_selector:
    description:
      - A selector to restrict results by labels.
    type: str
  field_selector:
    description:
      - A selector to filter based on object fields.
    type: str
  limit:
    description:
      - Maximum number of resources returned.
    type: int
  continue_token:
    description:
      - Use to retrieve the next set of available objects.
    type: str
extends_documentation_fragment:
  - flightctl.core.auth
requirements:
  - "flightctl (git+https://github.com/flightctl/flightctl-python-client.git)"
"""

EXAMPLES = r"""
- name: List all image builds
  flightctl.core.flightctl_image_builder_info:
    kind: ImageBuild
  register: builds

- name: Get a specific image build with exports
  flightctl.core.flightctl_image_builder_info:
    kind: ImageBuild
    name: my-build
    with_exports: true
  register: build

- name: Get build logs
  flightctl.core.flightctl_image_builder_info:
    kind: ImageBuild
    name: my-build
    log: true
  register: build_log

- name: List all image exports
  flightctl.core.flightctl_image_builder_info:
    kind: ImageExport
  register: exports

- name: Get export logs
  flightctl.core.flightctl_image_builder_info:
    kind: ImageExport
    name: my-export
    log: true
  register: export_log

- name: Download the exported artifact
  flightctl.core.flightctl_image_builder_info:
    kind: ImageExport
    name: my-export
    download: true
  register: export_artifact
"""

RETURN = r"""
result:
  description:
    - The resource(s), log content, or download artifact info.
  returned: success
  type: dict
  contains:
    data:
      description: List of resources.
      returned: When neither O(log) nor O(download) is set
      type: list
    log:
      description: The build/export log content.
      returned: When O(log=true)
      type: str
    download:
      description: Base64-encoded artifact content.
      returned: When O(download=true)
      type: str
    metadata:
      description: List metadata for pagination.
      returned: When listing resources
      type: dict
"""

from base64 import b64encode

from ..module_utils.imagebuilder_module import FlightctlImageBuilderModule
from ..module_utils.exceptions import FlightctlException


def _handle_image_build(module, name, fetch_log):
    if fetch_log:
        if not name:
            module.fail_json(msg="name is required when log=true")
        log_content = module.get_image_build_log(name)
        module.exit_json(result=dict(log=log_content))

    elif name:
        resource = module.get_image_build(
            name,
            with_exports=module.params.get("with_exports"),
        )
        if not resource:
            module.exit_json(result=dict(data=[]))
        module.exit_json(result=dict(data=[resource.to_dict()]))

    else:
        response = module.list_image_builds(
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
            limit=module.params.get("limit"),
            continue_token=module.params.get("continue_token"),
            with_exports=module.params.get("with_exports"),
        )
        result = dict(
            data=[item.to_dict() for item in response.items],
            metadata=response.metadata.to_dict() if response.metadata else {},
        )
        module.exit_json(result=result)


def _handle_image_export(module, name, fetch_log, fetch_download):
    if fetch_log and fetch_download:
        module.fail_json(msg="log and download are mutually exclusive")

    if fetch_log:
        if not name:
            module.fail_json(msg="name is required when log=true")
        log_content = module.get_image_export_log(name)
        module.exit_json(result=dict(log=log_content))

    elif fetch_download:
        if not name:
            module.fail_json(msg="name is required when download=true")
        artifact = module.download_image_export(name)
        encoded = b64encode(bytes(artifact)).decode('utf-8')
        module.exit_json(result=dict(download=encoded))

    elif name:
        resource = module.get_image_export(name)
        if not resource:
            module.exit_json(result=dict(data=[]))
        module.exit_json(result=dict(data=[resource.to_dict()]))

    else:
        response = module.list_image_exports(
            label_selector=module.params.get("label_selector"),
            field_selector=module.params.get("field_selector"),
            limit=module.params.get("limit"),
            continue_token=module.params.get("continue_token"),
        )
        result = dict(
            data=[item.to_dict() for item in response.items],
            metadata=response.metadata.to_dict() if response.metadata else {},
        )
        module.exit_json(result=result)


def main():
    argument_spec = dict(
        kind=dict(type="str", required=True, choices=["ImageBuild", "ImageExport"]),
        name=dict(type="str"),
        log=dict(type="bool", default=False),
        download=dict(type="bool", default=False),
        with_exports=dict(type="bool"),
        label_selector=dict(type="str"),
        field_selector=dict(type="str"),
        limit=dict(type="int"),
        continue_token=dict(type="str", no_log=True),
    )

    module = FlightctlImageBuilderModule(argument_spec=argument_spec)

    kind = module.params["kind"]
    name = module.params.get("name")
    fetch_log = module.params.get("log")
    fetch_download = module.params.get("download")

    try:
        if kind == "ImageBuild":
            if fetch_download:
                module.fail_json(msg="download is only supported for kind=ImageExport")
            _handle_image_build(module, name, fetch_log)
        else:
            _handle_image_export(module, name, fetch_log, fetch_download)

    except FlightctlException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()

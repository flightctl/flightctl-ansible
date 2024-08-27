#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import yaml
from typing import Dict, Any

from openapi_schema_validator import OAS30Validator

from .exceptions import ValidationException, FlightctlException
from .resource import create_definitions


def load_schema(file_path):
    with open(file_path, 'r') as file:
        schema = yaml.safe_load(file)
    return schema


def validate(definition: Dict[str, Any]) -> None:
    kind = definition["kind"]
    openapi_schema = load_schema("../../api/v1alpha1/openapi.yml")
    components = openapi_schema.get("components", {}).get("schemas", {})
    if kind not in components:
        raise ValueError(f"Component {kind} not found in the schema")

    component_schema = components[kind]
    validator = OAS30Validator(openapi_schema)

    try:
        validator.validate(definition, component_schema)
    except Exception as e:
        raise ValidationException(f"Validation error: {e.message}") from e


def get_definitions(params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        definitions = create_definitions(params)
    except Exception as e:
        msg = "Failed to load resource definition: {0}".format(e)
        raise FlightctlException(msg) from e

    return definitions


def run_module(module) -> None:
    results = []

    definitions = get_definitions(module.params)
    for definition in definitions:
        try:
            result = perform_action(module, definition)
        except Exception as e:
            raise FlightctlException(f"Failed to perform action: {e}") from e
        results.append(result)

    if len(results) == 1:
        module.result["result"] = results[0]
    else:
        module.result["results"] = results

    module.exit_json(**module.result)


def perform_action(module, definition: Dict[str, Any]) -> Dict[str, Any]:
    name = definition["metadata"].get("name")
    kind = definition.get("kind")
    state = module.params.get("state")
    result = {}
    params = {}

    if module.params.get("label_selector"):
        params["labelSelector"] = module.params["label_selector"]

    try:
        existing = module.get_one_or_many(kind, name=name, **params)
    except Exception as e:
        raise FlightctlException(f"Failed to get resource: {e}") from e

    if state == "absent":
        if existing:
            module.result["method"] = "delete"
            if module.check_mode:
                module.exit_json(**{"changed": True})

            module.result["changed"] = True

            try:
                result = module.delete(kind, name)
            except Exception as e:
                raise FlightctlException(f"Failed to delete resource: {e}") from e

    elif module.params["state"] == "present":
        # validate(definition)

        if existing:
            # Update not yet implemented
            pass
        else:
            module.result["method"] = "create"
            # Create a new resource
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                result = module.create(module.params, definition)
                module.result["changed"] = True
            except Exception as e:
                raise FlightctlException(f"Failed to create resource: {e}") from e

    return result

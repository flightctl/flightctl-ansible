# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as imp_exc:
    PYYAML_IMPORT_ERROR = imp_exc
else:
    PYYAML_IMPORT_ERROR = None

try:
    from openapi_schema_validator import OAS30Validator
except ImportError as imp_exc:
    OPENAPI_SCHEMA_IMPORT_ERROR = imp_exc
else:
    OPENAPI_SCHEMA_IMPORT_ERROR = None

from .api_module import FlightctlAPIModule
from .constants import CSR_KIND, ENROLLMENT_KIND
from .exceptions import FlightctlException, ValidationException
from .resources import create_definitions


def load_schema(file_path: str) -> Dict[str, Any]:
    """
    Loads an OpenAPI schema from a YAML file.

    Args:
        file_path (str): The path to the schema YAML file.

    Returns:
        Dict[str, Any]: The loaded schema as a dictionary.
    """
    if PYYAML_IMPORT_ERROR:
        raise PYYAML_IMPORT_ERROR
    with open(file_path, "r") as file:
        schema = yaml.safe_load(file)
    return schema


def validate(definition: Dict[str, Any]) -> None:
    """
    Validates a resource definition against an OpenAPI schema.

    Args:
        definition (Dict[str, Any]): The resource definition to validate.

    Raises:
        ValueError: If the resource kind is not found in the schema.
        ValidationException: If the validation fails.
    """
    if OPENAPI_SCHEMA_IMPORT_ERROR:
        raise OPENAPI_SCHEMA_IMPORT_ERROR

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
        raise ValidationException(f"Validation error: {e}") from e


def get_definitions(params: Dict[str, Any]) -> List:
    """
    Retrieves the resource definitions based on the provided parameters.

    Args:
        params (Dict[str, Any]): Parameters to load the resource definitions.

    Returns:
        Dict[str, Any]: The loaded resource definitions.

    Raises:
        FlightctlException: If loading the resource definitions fails.
    """
    try:
        definitions = create_definitions(params)
    except Exception as e:
        msg = f"Failed to load resource definition: {e}"
        raise FlightctlException(msg) from e

    return definitions


def run_module(module: Any) -> None:
    """
    Executes the module, performing actions based on resource definitions.

    Args:
        module (Any): The Ansible module instance.

    Raises:
        FlightctlException: If an action fails.
    """
    results: List[Dict[str, Any]] = []

    definitions = get_definitions(module.params)
    for definition in definitions:
        try:
            changed, result = perform_action(module, definition)
            module.result["changed"] |= changed
        except Exception as e:
            raise FlightctlException(f"Failed to perform action: {e}") from e
        results.append(result)

    if len(results) == 1:
        module.result["result"] = results[0]
    else:
        module.result["results"] = results

    module.exit_json(**module.result)


def perform_action(module, definition: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Performs the appropriate action (create, update, delete) on a resource.

    Args:
        module (Any): The Ansible module instance.
        definition (Dict[str, Any]): The resource definition.

    Returns:
        Tuple[bool, Dict[str, Any]]: A tuple containing a boolean indicating if the resource
        was changed and the result of the action.

    Raises:
        ValidationException: If necessary definition parameters do not exist.
        FlightctlException: If performing the action fails.
    """
    if definition["metadata"].get("name") is None:
        raise ValidationException("A name must be specified")

    if definition.get("kind") is None:
        raise ValidationException("A kind value must be specified")

    name = definition["metadata"]["name"]
    kind = definition["kind"]
    state = module.params.get("state")
    params = {}
    result: Dict[str, Any] = {}
    changed: bool = False

    if module.params.get("label_selector"):
        params["labelSelector"] = module.params["label_selector"]

    try:
        existing = module.get_one_or_many(kind, name=name, **params)
    except Exception as e:
        raise FlightctlException(f"Failed to get resource: {e}") from e

    if state == "absent":
        if existing:
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                changed, result = module.delete(kind, name)
            except Exception as e:
                raise FlightctlException(f"Failed to delete resource: {e}") from e

    elif module.params["state"] == "present":
        # validate(definition)

        if existing:
            # Update resource
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                changed, result = module.update(existing[0], definition)
            except Exception as e:
                raise FlightctlException(f"Failed to update resource: {e}") from e
        else:
            # Create a new resource
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                changed, result = module.create(definition)
            except Exception as e:
                raise FlightctlException(f"Failed to create resource: {e}") from e

    return changed, result


def perform_approval(module: FlightctlAPIModule, kind: str, name: str, payload: Dict[str, Any]) -> None:
    """
    Performs the approval action on a specific resource.

    Args:
        module (FlightctlAPIModule): The FlightctlAPIModule instance to act upon.
        kind: Resource kind.
        name: Resource name identifier.
        payload: Data that will be passed to the approval request.

    Raises:
        ValidationException: If necessary definition parameters do not exist.
        FlightctlException: If performing the action fails.
    """
    if not kind:
        raise ValidationException("A kind must be specified.")
    elif kind not in [CSR_KIND, ENROLLMENT_KIND]:
        raise ValidationException(f"Kind {kind} does not support approval.")

    if not name:
        raise ValidationException("A name must be specified.")

    if payload.get('approved', None) is None:
        raise ValidationException("Approval value must be specified.")

    try:
        existing = module.get_endpoint(kind, name)
        approved = None
        if kind == ENROLLMENT_KIND:
            approved = existing.json.get('status', {}).get('approval', {}).get('approved', None)
        elif kind == CSR_KIND:
            conditions = existing.json.get('status', {}).get('conditions', [])
            approval_condition = next((c for c in conditions if c.get('type') == "Approved"), None)
            if approval_condition is not None:
                approved = bool(approval_condition['status'])

        if approved == payload.get('approved'):
            module.exit_json(**{"changed": False})
            return
    except Exception as e:
        raise FlightctlException(f"Failed to get resource: {e}") from e

    if module.check_mode:
        module.exit_json(**{"changed": True})
        return

    try:
        module.approve(kind, name, **payload)
    except Exception as e:
        raise FlightctlException(f"Failed to approve resource: {e}") from e

    module.exit_json(**{"changed": True})

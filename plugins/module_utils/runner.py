# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from typing import Any, Dict, List, Tuple

from .api_module import FlightctlAPIModule
from .constants import ResourceType
from .exceptions import FlightctlException, ValidationException
from .options import ApprovalOptions, GetOptions
from .resources import create_definitions

try:
    from flightctl.models.enrollment_request import EnrollmentRequest
    from flightctl.models.certificate_signing_request import CertificateSigningRequest
except ImportError as imp_exc:
    CLIENT_IMPORT_ERROR = imp_exc
else:
    CLIENT_IMPORT_ERROR = None


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
    try:
        resource = ResourceType(definition.get("kind"))
    except (TypeError, ValueError):
        raise ValidationException(f"Invalid Kind {module.params.get('kind')}")

    name = definition["metadata"].get("name")
    fleet_name = module.params.get("fleet_name")
    label_selector = module.params.get("label_selector")
    state = module.params.get("state")
    changed: bool = False
    result = None

    try:
        get_options = GetOptions(
            resource=resource,
            name=name,
            fleet_name=fleet_name,
            label_selector=label_selector,
        )
        existing_result = module.get_one_or_many(get_options)
    except Exception as e:
        raise FlightctlException(f"Failed to get resource: {e}") from e

    if state == "absent":
        if existing_result.data:
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                result = module.delete(resource, name, fleet_name)
                changed |= True
            except Exception as e:
                raise FlightctlException(f"Failed to delete resource: {e}") from e

    elif state == "present":
        if existing_result.data:
            # Update resource
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                if module.params.get("force_update"):
                    result = module.replace(resource, definition)
                    changed |= True
                else:
                    changed, result = module.update(resource, existing_result.data[0], definition)
            except Exception as e:
                raise FlightctlException(f"Failed to update resource: {e}") from e
        else:
            # Create a new resource
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                result = module.create(resource, definition)
                changed |= True
            except Exception as e:
                raise FlightctlException(f"Failed to create resource: {e}") from e

    elif state == "decommission":  # Handle decommissioning
        if resource != ResourceType.DEVICE:
            raise ValidationException(f"Decommissioning is only allowed for devices, not {resource}.")

        if existing_result.data:
            if module.check_mode:
                module.exit_json(**{"changed": True})

            try:
                result = module.decommission(name, definition)
                changed |= True
            except Exception as e:
                raise FlightctlException(f"Failed to decommission device: {e}") from e
        else:
            raise FlightctlException(f"Device '{name}' not found for decommissioning.")

    if result is None:
        raise FlightctlException("No result returned from operation.")

    return changed, result.to_dict()


def perform_approval(module: FlightctlAPIModule) -> None:
    """
    Performs the approval action on a specific resource.

    Args:
        module (FlightctlAPIModule): The FlightctlAPIModule instance to act upon.

    Raises:
        ValidationException: If necessary definition parameters do not exist.
        FlightctlException: If performing the action fails.
    """
    if CLIENT_IMPORT_ERROR:
        raise CLIENT_IMPORT_ERROR

    try:
        resource = ResourceType(module.params.get("kind"))
    except (TypeError, ValueError):
        raise ValidationException(f"Invalid Kind {module.params.get('kind')}")

    approval_options = ApprovalOptions(
        resource=resource,
        name=module.params.get("name"),
        approved=module.params.get("approved"),
        approved_by=module.params.get("approved_by"),
        labels=module.params.get("labels")
    )

    try:
        get_options = GetOptions(
            resource=resource,
            name=approval_options.name,
        )
        existing = module.get(get_options)
        currently_approved = None
        if isinstance(existing, EnrollmentRequest):
            try:
                currently_approved = existing.status.approval.approved
            except AttributeError:
                pass
        elif isinstance(existing, CertificateSigningRequest):
            try:
                conditions = existing.status.conditions
                approval_condition = next((c for c in conditions if c.type == "Approved"), None)
                if approval_condition is not None:
                    # The api returns string values for booleans in the conditions
                    if approval_condition.status == 'True':
                        currently_approved = True
                    elif approval_condition.status == 'False':
                        currently_approved = False
            except AttributeError:
                pass

        if approval_options.approved == currently_approved:
            module.exit_json(**{"changed": False})
            return
    except Exception as e:
        raise FlightctlException(f"Failed to get resource: {e}") from e

    if module.check_mode:
        module.exit_json(**{"changed": True})
        return

    try:
        module.approve(approval_options)
    except Exception as e:
        raise FlightctlException(f"Failed to approve resource: {e}") from e

    module.exit_json(**{"changed": True})

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock

from plugins.module_utils.api_module import ListResult
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException, FlightctlApiException, ValidationException
from plugins.module_utils.runner import perform_action, perform_approval

from flightctl.models.enrollment_request import EnrollmentRequest
from flightctl.models.certificate_signing_request import CertificateSigningRequest


@pytest.fixture
def mock_module():
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {}
    mock_module = MagicMock()
    mock_module.get_endpoint.return_value = mock_get_response
    mock_module.check_mode = False

    # Input parameters
    mock_module.params = {
        "kind": ResourceType.ENROLLMENT.value,
        "name": "test-resource",
        "approved": True,
    }

    return mock_module


@pytest.fixture
def enrollment_hook_policy_module():
    module = MagicMock()
    module.check_mode = False
    module.params = {
        "kind": ResourceType.ENROLLMENT_HOOK_POLICY.value,
        "name": "test-enrollment-hook-policy",
        "fleet_name": None,
        "catalog_name": None,
        "label_selector": None,
        "state": "present",
        "force_update": False,
    }
    return module


@pytest.fixture
def enrollment_hook_policy_definition():
    return {
        "apiVersion": "flightctl.io/v1beta1",
        "kind": "EnrollmentHookPolicy",
        "metadata": {"name": "test-enrollment-hook-policy"},
        "spec": {
            "afterEnrolling": {
                "failurePolicy": "Continue",
                "controlPlaneActions": [
                    {"url": "https://example.com/hooks/enrollment"}
                ],
            }
        },
    }


def test_perform_action_accepts_enrollment_hook_policy(
        enrollment_hook_policy_module, enrollment_hook_policy_definition):
    response = MagicMock()
    response.to_dict.return_value = enrollment_hook_policy_definition
    enrollment_hook_policy_module.get_one_or_many.return_value = ListResult(data=[])
    enrollment_hook_policy_module.create.return_value = response

    changed, result = perform_action(
        enrollment_hook_policy_module,
        enrollment_hook_policy_definition,
    )

    get_options = enrollment_hook_policy_module.get_one_or_many.call_args.args[0]
    assert get_options.resource is ResourceType.ENROLLMENT_HOOK_POLICY
    enrollment_hook_policy_module.create.assert_called_once_with(
        ResourceType.ENROLLMENT_HOOK_POLICY,
        enrollment_hook_policy_definition,
        None,
    )
    assert changed is True
    assert result == enrollment_hook_policy_definition


@pytest.mark.parametrize(
    ("state", "existing_data"),
    [
        pytest.param("present", [], id="create"),
        pytest.param("present", [MagicMock()], id="update"),
        pytest.param("absent", [MagicMock()], id="delete"),
    ],
)
def test_perform_action_enrollment_hook_policy_check_mode_does_not_mutate(
        enrollment_hook_policy_module, enrollment_hook_policy_definition,
        state, existing_data):
    enrollment_hook_policy_module.params["state"] = state
    enrollment_hook_policy_module.check_mode = True
    enrollment_hook_policy_module.get_one_or_many.return_value = ListResult(
        data=existing_data
    )
    enrollment_hook_policy_module.exit_json.side_effect = SystemExit

    with pytest.raises(SystemExit):
        perform_action(
            enrollment_hook_policy_module,
            enrollment_hook_policy_definition,
        )

    enrollment_hook_policy_module.exit_json.assert_called_once_with(changed=True)
    enrollment_hook_policy_module.create.assert_not_called()
    enrollment_hook_policy_module.update.assert_not_called()
    enrollment_hook_policy_module.replace.assert_not_called()
    enrollment_hook_policy_module.delete.assert_not_called()


def test_perform_action_enrollment_hook_policy_wraps_get_failure(
        enrollment_hook_policy_module, enrollment_hook_policy_definition):
    enrollment_hook_policy_module.get_one_or_many.side_effect = (
        FlightctlApiException("server error")
    )

    with pytest.raises(FlightctlException, match="Failed to get resource: server error"):
        perform_action(
            enrollment_hook_policy_module,
            enrollment_hook_policy_definition,
        )


@pytest.mark.parametrize(
    ("state", "existing_data", "method", "error_match"),
    [
        pytest.param("present", [], "create", "Failed to create resource", id="create"),
        pytest.param(
            "present", [MagicMock()], "update", "Failed to update resource", id="update"
        ),
        pytest.param(
            "absent", [MagicMock()], "delete", "Failed to delete resource", id="delete"
        ),
    ],
)
def test_perform_action_enrollment_hook_policy_wraps_mutation_failure(
        enrollment_hook_policy_module, enrollment_hook_policy_definition,
        state, existing_data, method, error_match):
    enrollment_hook_policy_module.params["state"] = state
    enrollment_hook_policy_module.get_one_or_many.return_value = ListResult(
        data=existing_data
    )
    getattr(enrollment_hook_policy_module, method).side_effect = (
        FlightctlApiException("server error")
    )

    with pytest.raises(FlightctlException, match=f"{error_match}: server error"):
        perform_action(
            enrollment_hook_policy_module,
            enrollment_hook_policy_definition,
        )


def test_perform_approval__get_endpoint_failure(mock_module):
    mock_module.get.side_effect = FlightctlApiException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to get resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_not_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_failure(mock_module):
    mock_module.approve.side_effect = FlightctlApiException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to approve resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_of_already_approved_enrollment_returns_early(mock_module):
    mock_approval = MagicMock()
    mock_approval.approved = True
    mock_status = MagicMock()
    mock_status.approval = mock_approval
    mock_approved_enrollment_response = MagicMock(spec=EnrollmentRequest)
    mock_approved_enrollment_response.status = mock_status
    mock_module.get.return_value = mock_approved_enrollment_response

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__approval_of_already_approved_csr_returns_early(mock_module):
    mock_conditions = [MagicMock(type="Approved", status="True")]
    mock_status = MagicMock()
    mock_status.conditions = mock_conditions
    mock_csr_response = MagicMock(spec=CertificateSigningRequest)
    mock_csr_response.status = mock_status
    mock_module.get.return_value = mock_csr_response

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__check_mode_does_not_call_approve(mock_module):
    mock_module.check_mode = True

    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval(mock_module):
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval_with_false_value(mock_module):
    mock_module.params["approved"] = False
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_csr_approval(mock_module):
    mock_module.params["kind"] = ResourceType.CSR.value
    perform_approval(mock_module)
    mock_module.get.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__no_kind(mock_module):
    mock_module.params["kind"] = None
    with pytest.raises(ValidationException, match="Invalid Kind None"):
        perform_approval(mock_module)


def test_perform_approval__invalid_kind(mock_module):
    mock_module.params["kind"] = "InvalidKind"
    with pytest.raises(ValidationException, match="Invalid Kind InvalidKind"):
        perform_approval(mock_module)


def test_perform_approval__no_name(mock_module):
    mock_module.params["name"] = ""
    with pytest.raises(ValidationException, match="Name must be specified"):
        perform_approval(mock_module)


def test_perform_approval__no_approval(mock_module):
    mock_module.params["approved"] = None
    with pytest.raises(ValidationException, match="Approved must be specified"):
        perform_approval(mock_module)

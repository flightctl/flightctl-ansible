from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock

import pytest

from plugins.module_utils.constants import Kind
from plugins.module_utils.exceptions import (
    FlightctlException,
    FlightctlHTTPException,
    ValidationException,
)
from plugins.module_utils.runner import perform_approval


@pytest.fixture
def mock_module():
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {}
    mock_module = MagicMock()
    mock_module.get_endpoint.return_value = mock_get_response
    mock_module.check_mode = False

    # Input parameters
    mock_module.params = {
        "kind": Kind.ENROLLMENT.value,
        "name": "test-resource",
        "approved": True,
    }

    return mock_module


def test_perform_approval__get_endpoint_failure(mock_module):
    mock_module.get_endpoint.side_effect = FlightctlHTTPException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to get resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_not_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_failure(mock_module):
    mock_module.approve.side_effect = FlightctlHTTPException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to approve resource: .*"):
        perform_approval(mock_module)
        mock_module.approve.assert_called()
        mock_module.exit_json.assert_not_called()


def test_perform_approval__approval_of_already_approved_enrollment_returns_early(
    mock_module,
):
    mock_approved_enrollment_response = MagicMock()
    mock_approved_enrollment_response.json.get.return_value = {
        "approval": {"approved": True}
    }
    mock_module.get_endpoint.return_value = mock_approved_enrollment_response

    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__approval_of_already_approved_csr_returns_early(mock_module):
    mock_approved_csr_response = MagicMock()
    mock_approved_csr_response.json.get.return_value = {
        "conditions": [{"type": "Approved", "status": "True"}]
    }
    mock_module.get_endpoint.return_value = mock_approved_csr_response
    mock_module.params["kind"] = Kind.CSR.value

    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)


def test_perform_approval__check_mode_does_not_call_approve(mock_module):
    mock_module.check_mode = True

    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval(mock_module):
    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_enrollment_approval_with_false_value(mock_module):
    mock_module.params["approved"] = False
    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)


def test_perform_approval__successful_csr_approval(mock_module):
    mock_module.params["kind"] = Kind.CSR.value
    perform_approval(mock_module)
    mock_module.get_endpoint.assert_called()
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

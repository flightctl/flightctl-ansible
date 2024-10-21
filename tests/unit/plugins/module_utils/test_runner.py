import pytest
from unittest.mock import MagicMock

from plugins.module_utils.constants import CSR_KIND, ENROLLMENT_KIND
from plugins.module_utils.runner import perform_approval
from plugins.module_utils.exceptions import FlightctlException, FlightctlHTTPException, ValidationException


@pytest.fixture
def mock_module():
    mock_get_response = MagicMock()
    mock_get_response.json.return_value = {}
    mock_module = MagicMock()
    mock_module.get_endpoint.return_value = mock_get_response
    mock_module.check_mode = False
    return mock_module

def test_perform_approval__get_endpoint_failure(mock_module):
    mock_module.get_endpoint.side_effect = FlightctlHTTPException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to get resource: .*"):
        perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": True})
        mock_module.approve.assert_not_called()
        mock_module.exit_json.assert_not_called()

def test_perform_approval__approval_failure(mock_module):
    mock_module.approve.side_effect = FlightctlHTTPException("Oh No!")
    with pytest.raises(FlightctlException, match="Failed to approve resource: .*"):
        perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": True})
        mock_module.approve.assert_called()
        mock_module.exit_json.assert_not_called()

def test_perform_approval__approval_of_already_approved_enrollment_returns_early(mock_module):
    mock_approved_enrollment_response = MagicMock()
    mock_approved_enrollment_response.json.get.return_value = {"approval": {"approved": True}}
    mock_module.get_endpoint.return_value = mock_approved_enrollment_response

    perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": True})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)

def test_perform_approval__approval_of_already_approved_csr_returns_early(mock_module):
    mock_approved_csr_response = MagicMock()
    mock_approved_csr_response.json.get.return_value = {"conditions": [{"type": "Approved", "status": "True"}]}
    mock_module.get_endpoint.return_value = mock_approved_csr_response

    perform_approval(mock_module, CSR_KIND, "test-name", {"approved": True})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=False)

def test_perform_approval__check_mode_does_not_call_approve(mock_module):
    mock_module.check_mode = True

    perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": True})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_not_called()
    mock_module.exit_json.assert_called_with(changed=True)

def test_perform_approval__successful_enrollment_approval(mock_module):
    perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": True})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)

def test_perform_approval__successful_enrollment_approval_with_false_value(mock_module):
    perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {"approved": False})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)

def test_perform_approval__successful_csr_approval(mock_module):
    perform_approval(mock_module, CSR_KIND, "test-name", {"approved": True})
    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called_with(changed=True)

def test_perform_approval__no_kind():
    with pytest.raises(ValidationException, match="A kind must be specified."):
        perform_approval({}, None, "test-name", {"approved": True})

def test_perform_approval__invalid_kind():
    with pytest.raises(ValidationException, match="Kind InvalidKind does not support approval."):
        perform_approval({}, "InvalidKind", "test-name", {"approved": True})

def test_perform_approval__no_name():
    with pytest.raises(ValidationException, match="A name must be specified."):
        perform_approval({}, ENROLLMENT_KIND, "", {"approved": True})

def test_perform_approval__no_approval():
    with pytest.raises(ValidationException, match="Approval value must be specified."):
        perform_approval({}, ENROLLMENT_KIND, "test-name", {})

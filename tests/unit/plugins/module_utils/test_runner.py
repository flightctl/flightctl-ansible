import pytest
from unittest.mock import Mock

from plugins.module_utils.constants import CSR_KIND, ENROLLMENT_KIND
from plugins.module_utils.runner import perform_approval

def test_perform_approval():
    mock_get_response = Mock()
    mock_get_response.json.return_value = {}
    mock_module = Mock()
    mock_module.get_endpoint.return_value = mock_get_response
    mock_module.check_mode = False

    perform_approval(mock_module, ENROLLMENT_KIND, "test-name", {'approved': True})

    mock_module.get_endpoint.assert_called()
    mock_module.approve.assert_called()
    mock_module.exit_json.assert_called()

# module.fail_json.assert_not_called()
    # exit_json
    # get_endpoint
    # approve
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.inputs import ApprovalInput

from plugins.module_utils.api_client.models.enrollment_request_approval import EnrollmentRequestApproval


@pytest.fixture
def api_module():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client.yaml'
    ))
    return FlightctlAPIModule(argument_spec={})


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_success(MockEnrollmentrequestApi, api_module):
    mock_api_instance = MagicMock()
    MockEnrollmentrequestApi.return_value = mock_api_instance

    input = ApprovalInput(ResourceType.ENROLLMENT, "test-enrollment", True)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body)


# def test_approve_404(api_module):
#     mock_response = Mock()
#     mock_response.status = 404
#     mock_response.json = {}
#     mock_request = Mock(return_value=mock_response)
#     api_module.request = mock_request

#     input = ApprovalInput(ResourceType.ENROLLMENT, "test-enrollment", True)
#     with pytest.raises(FlightctlException, match="Unable to approve EnrollmentRequest for test-enrollment"):
#         api_module.approve(input)


# def test_approve_csr(api_module):
#     mock_response = Mock()
#     mock_response.status = 200
#     mock_request = Mock(return_value=mock_response)
#     api_module.request = mock_request

#     input = ApprovalInput(ResourceType.CSR, "test-csr", True)
#     api_module.approve(input)
#     mock_request.assert_called_with("POST", "https://test-flightctl-url.com/api/v1/certificatesigningrequests/test-csr/approval", **input.to_request_params())


# def test_deny_csr(api_module):
#     mock_response = Mock()
#     mock_response.status = 200
#     mock_request = Mock(return_value=mock_response)
#     api_module.request = mock_request

#     input = ApprovalInput(ResourceType.CSR, "test-csr", False)
#     api_module.approve(input)
#     mock_request.assert_called_with("DELETE", "https://test-flightctl-url.com/api/v1/certificatesigningrequests/test-csr/approval")

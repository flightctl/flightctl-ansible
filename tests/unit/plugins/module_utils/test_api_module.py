from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.options import ApprovalOptions

from openapi_client.exceptions import NotFoundException
from openapi_client.models.enrollment_request_approval import EnrollmentRequestApproval


@pytest.fixture
def api_module():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client.yaml'
    ))
    return FlightctlAPIModule(argument_spec={})


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_deny_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", False)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_404(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_api_instance.approve_enrollment_request.side_effect = NotFoundException()

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    with pytest.raises(FlightctlException, match="Unable to approve EnrollmentRequest - test-enrollment: *"):
        api_module.approve(input)


@patch('plugins.module_utils.api_module.DefaultApi')
def test_approve_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module.approve(input)
    mock_api_instance.approve_certificate_signing_request.assert_called_with(input.name)


@patch('plugins.module_utils.api_module.DefaultApi')
def test_approve_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.CSR, "test-csr", False)
    api_module.approve(input)
    mock_api_instance.deny_certificate_signing_request.assert_called_with(input.name)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.constants import ResourceType
from plugins.module_utils.exceptions import FlightctlException
from plugins.module_utils.options import ApprovalOptions

from flightctl.exceptions import NotFoundException
from flightctl.models.enrollment_request_approval import EnrollmentRequestApproval
from flightctl.models.certificate_signing_request import CertificateSigningRequest


@pytest.fixture
def api_module():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client.yaml'
    ))
    return FlightctlAPIModule(argument_spec={})


@pytest.fixture
def api_module_with_token():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_token='test-token'
    ))
    return FlightctlAPIModule(argument_spec={})


@pytest.fixture
def api_module_with_user_pass():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_username='test-user',
        flightctl_password='test-pass'
    ))
    return FlightctlAPIModule(argument_spec={})


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_deny_enrollment_success(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", False)
    body = EnrollmentRequestApproval.from_dict(input.to_request_params())
    api_module.approve(input)
    mock_api_instance.approve_enrollment_request.assert_called_with(input.name, body, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.EnrollmentrequestApi')
def test_approve_404(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_api_instance.approve_enrollment_request.side_effect = NotFoundException()

    input = ApprovalOptions(ResourceType.ENROLLMENT, "test-enrollment", True)
    with pytest.raises(FlightctlException, match="Unable to approve EnrollmentRequest - test-enrollment: *"):
        api_module.approve(input)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_approve_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.read_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(input.name, mock_csr, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_deny_csr(mock_api, api_module):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.read_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", False)
    api_module.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(input.name, mock_csr, _headers=None, _request_timeout=10)


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_token_auth(mock_api, api_module_with_token):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.read_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module_with_token.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(
        input.name,
        mock_csr,
        _headers={'Authorization': 'Bearer test-token'},
        _request_timeout=10
    )


@patch('plugins.module_utils.api_module.CertificatesigningrequestApi')
def test_basic_auth(mock_api, api_module_with_user_pass):
    mock_api_instance = MagicMock()
    mock_api.return_value = mock_api_instance
    mock_csr = MagicMock(spec=CertificateSigningRequest)
    mock_csr.status = MagicMock()

    mock_api_instance.read_certificate_signing_request.return_value = mock_csr

    input = ApprovalOptions(ResourceType.CSR, "test-csr", True)
    api_module_with_user_pass.approve(input)
    mock_api_instance.update_certificate_signing_request_approval.assert_called_with(
        input.name,
        mock_csr,
        _headers={'Authorization': 'Basic dGVzdC11c2VyOnRlc3QtcGFzcw=='},
        _request_timeout=10
    )

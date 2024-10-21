import pytest
from unittest.mock import Mock

from tests.unit.utils import set_module_args

from plugins.module_utils.api_module import FlightctlAPIModule
from plugins.module_utils.exceptions import FlightctlException


@pytest.fixture
def api_module():
    set_module_args(dict(
        flightctl_host='https://test-flightctl-url.com/',
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client.yaml'
    ))
    return FlightctlAPIModule(argument_spec={})

def test_build_url_with_valid_endpoint(api_module):
    url = api_module.build_url('device')
    assert url.geturl() == 'https://test-flightctl-url.com/api/v1/devices'

def test_build_url_with_valid_endpoint_and_name(api_module):
    url = api_module.build_url('device', 'awesome-device-1')
    assert url.geturl() == 'https://test-flightctl-url.com/api/v1/devices/awesome-device-1'

def test_build_url_with_invalid_endpoint(api_module):
    with pytest.raises(FlightctlException, match="Invalid 'kind' specified: widget"):
        api_module.build_url('widget')

def test_approve_success(api_module):
    mock_response = Mock()
    mock_response.status = 200
    mock_request = Mock(return_value=mock_response)
    api_module.request = mock_request

    params = {"approved": True}
    api_module.approve("EnrollmentRequest", "test-device", **params)
    mock_request.assert_called_with("POST", "https://test-flightctl-url.com/api/v1/enrollmentrequests/test-device/approval", **params)

def test_approve_404(api_module):
    mock_response = Mock()
    mock_response.status = 404
    mock_response.json = {}
    mock_request = Mock(return_value=mock_response)
    api_module.request = mock_request

    params = {"approved": True}
    with pytest.raises(FlightctlException, match="Unable to approve EnrollmentRequest for test-device"):
        api_module.approve("EnrollmentRequest", "test-device", **params)

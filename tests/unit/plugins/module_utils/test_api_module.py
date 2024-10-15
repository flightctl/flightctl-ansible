import pytest

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

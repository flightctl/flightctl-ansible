from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest

from tests.unit.utils import set_module_args

from plugins.module_utils.core import FlightctlModule


@pytest.fixture
def module_with_ca_file():
    set_module_args(dict(
        flightctl_config_file='tests/unit/plugins/module_utils/fixtures/client_with_ca_data.yaml'
    ))
    return FlightctlModule(argument_spec={})


def test_build_url_with_valid_endpoint(module_with_ca_file):
    assert module_with_ca_file.ca_path
    with open(module_with_ca_file.ca_path, 'r') as f:
        certificate_content = f.read()

    with open('tests/unit/plugins/module_utils/fixtures/test_ca.crt', 'r') as f:
        expected_content = f.read()

    assert certificate_content == expected_content

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
from unittest.mock import patch

from plugins.module_utils.exceptions import FlightctlException
from tests.unit.utils import set_module_args


APPLICATION_MODULE_PATH = "plugins.modules.flightctl_application"
API_MODULE_PATH = "plugins.module_utils.api_module.FlightctlAPIModule"


def _application_params(**overrides):
    params = {
        "flightctl_host": "https://flightctl.example.com",
        "flightctl_token": "token",
        "kind": "Device",
        "name": "edge-1",
        "app_name": "workload",
        "state": "started",
    }
    params.update(overrides)
    return params


@pytest.mark.parametrize(
    ("kind", "name", "app_name", "state"),
    [
        ("Device", "edge-1", "workload", "started"),
        ("Fleet", "fleet-a", "workload", "stopped"),
    ],
)
def test_application_module_delegates_valid_device_and_fleet_actions(
    kind, name, app_name, state
):
    set_module_args(
        _application_params(kind=kind, name=name, app_name=app_name, state=state)
    )

    with patch(f"{APPLICATION_MODULE_PATH}.perform_application_action") as perform_action:
        from plugins.modules.flightctl_application import main

        main()

    module = perform_action.call_args.args[0]
    assert module.params["kind"] == kind
    assert module.params["name"] == name
    assert module.params["app_name"] == app_name
    assert module.params["state"] == state


@pytest.mark.parametrize("required_param", ["kind", "name", "app_name", "state"])
def test_application_module_requires_all_action_parameters(required_param):
    params = _application_params()
    del params[required_param]
    set_module_args(params)

    with patch(f"{API_MODULE_PATH}.fail_json") as fail_json:
        fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            from plugins.modules.flightctl_application import main

            main()

    assert required_param in fail_json.call_args.kwargs["msg"]


def test_application_module_reports_action_failures():
    set_module_args(_application_params())

    with patch(
        f"{APPLICATION_MODULE_PATH}.perform_application_action",
        side_effect=FlightctlException("action error"),
    ), patch(f"{API_MODULE_PATH}.fail_json") as fail_json:
        fail_json.side_effect = SystemExit(1)
        with pytest.raises(SystemExit):
            from plugins.modules.flightctl_application import main

            main()

    assert fail_json.call_args.kwargs["msg"] == "Failed application action: action error"

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest
from flightctl.exceptions import ApiException

from plugins.module_utils.exceptions import FlightctlException

MODULE_PATH = "plugins.modules.flightctl_enrollment_hook_override"
API_CLASS = f"{MODULE_PATH}.DeviceApi"
MODULE_CLASS = f"{MODULE_PATH}.FlightctlAPIModule"
RAW_RESPONSE_TO_DICT = f"{MODULE_PATH}.raw_response_to_dict"


def _mock_module(name="device-1", check_mode=False):
    module = MagicMock()
    module.params = {"name": name}
    module.check_mode = check_mode
    module.client = MagicMock()
    module.exit_json.side_effect = SystemExit(0)
    return module


def test_override_enrollment_hook_returns_device():
    module = _mock_module()
    api = MagicMock()
    response = MagicMock()
    result = {"metadata": {"name": "device-1"}}
    module.call_api.return_value = response

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(API_CLASS, return_value=api),
        patch(RAW_RESPONSE_TO_DICT, return_value=result) as raw_response_to_dict,
    ):
        from plugins.modules.flightctl_enrollment_hook_override import main

        with pytest.raises(SystemExit):
            main()

    module.call_api.assert_called_once_with(
        api.override_device_enrollment_hook_without_preload_content,
        "device-1",
    )
    raw_response_to_dict.assert_called_once_with(response)
    api.override_device_enrollment_hook.assert_not_called()
    module.exit_json.assert_called_once_with(
        changed=True,
        result=result,
    )


def test_override_enrollment_hook_check_mode_does_not_call_api():
    module = _mock_module(check_mode=True)

    with patch(MODULE_CLASS, return_value=module), patch(API_CLASS) as api_class:
        from plugins.modules.flightctl_enrollment_hook_override import main

        with pytest.raises(SystemExit):
            main()

    api_class.assert_not_called()
    module.call_api.assert_not_called()
    module.exit_json.assert_called_once_with(changed=True)


def test_override_enrollment_hook_requires_device_name():
    module = _mock_module(name=None)
    module.fail_json.side_effect = SystemExit(1)

    with patch(MODULE_CLASS, return_value=module), patch(API_CLASS):
        from plugins.modules.flightctl_enrollment_hook_override import main

        with pytest.raises(SystemExit):
            main()

    module.fail_json.assert_called_once_with(msg="name is required")


@pytest.mark.parametrize(
    "error",
    [
        ApiException(status=404, reason="device not found"),
        ApiException(status=403, reason="forbidden"),
        FlightctlException("connection failed"),
    ],
)
def test_override_enrollment_hook_wraps_api_errors(error):
    module = _mock_module()
    module.call_api.side_effect = error
    module.fail_json.side_effect = SystemExit(1)

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(API_CLASS, return_value=MagicMock()),
    ):
        from plugins.modules.flightctl_enrollment_hook_override import main

        with pytest.raises(SystemExit):
            main()

    module.fail_json.assert_called_once()
    assert (
        "Failed to override enrollment hook" in module.fail_json.call_args.kwargs["msg"]
    )

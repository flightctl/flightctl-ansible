from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest
from flightctl.exceptions import ApiException

from plugins.module_utils.exceptions import FlightctlException

MODULE_PATH = "plugins.modules.flightctl_label_sync_provenance_info"
MODULE_CLASS = f"{MODULE_PATH}.FlightctlAPIModule"
DEVICE_API_CLASS = f"{MODULE_PATH}.DeviceApi"
LABELSYNCMAPPING_API_CLASS = f"{MODULE_PATH}.LabelsyncmappingApi"
RAW_RESPONSE_TO_DICT = f"{MODULE_PATH}.raw_response_to_dict"


def _mock_module(params, check_mode=False):
    module = MagicMock()
    module.params = params
    module.check_mode = check_mode
    module.client = MagicMock()
    module.exit_json.side_effect = SystemExit(0)
    module.fail_json.side_effect = SystemExit(1)
    return module


def test_device_provenance_query_returns_items():
    module = _mock_module({"name": "device-1", "label_keys": None})
    api = MagicMock()
    result = {"items": [{"key": "example.com/site", "owners": ["mapping-1"]}]}
    response = MagicMock()
    response.to_dict.return_value = result
    module.call_api.return_value = response

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(DEVICE_API_CLASS, return_value=api),
        patch(LABELSYNCMAPPING_API_CLASS) as labelsyncmapping_api,
        patch(RAW_RESPONSE_TO_DICT, return_value=result) as raw_response_to_dict,
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    module.call_api.assert_called_once_with(
        api.get_device_label_sync_provenance,
        "device-1",
    )
    raw_response_to_dict.assert_not_called()
    api.get_device_label_sync_provenance_without_preload_content.assert_not_called()
    labelsyncmapping_api.assert_not_called()
    module.exit_json.assert_called_once_with(result=result)


def test_organization_provenance_query_preserves_duplicate_keys():
    label_keys = ["example.com/site", "example.com/site", "example.com/tier"]
    module = _mock_module({"name": None, "label_keys": label_keys}, check_mode=True)
    api = MagicMock()
    result = {
        "items": [
            {"key": "example.com/site", "owners": ["mapping-1"]},
            {"key": "example.com/site", "owners": ["mapping-1"]},
            {"key": "example.com/tier", "owners": []},
        ]
    }
    response = MagicMock()
    response.to_dict.return_value = result
    module.call_api.return_value = response

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(LABELSYNCMAPPING_API_CLASS, return_value=api),
        patch(DEVICE_API_CLASS) as device_api,
        patch(RAW_RESPONSE_TO_DICT, return_value=result),
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    module.call_api.assert_called_once_with(
        api.get_label_sync_provenance,
        label_keys,
    )
    api.get_label_sync_provenance_without_preload_content.assert_not_called()
    device_api.assert_not_called()
    module.exit_json.assert_called_once_with(result=result)


def test_pydantic_response_validation_uses_raw_fallback_once():
    module = _mock_module({"name": "device-1", "label_keys": None})
    api = MagicMock()
    raw_response = MagicMock()
    result = {"items": []}

    class ValidationError(Exception):
        __module__ = "pydantic_core._pydantic_core"

    module.call_api.side_effect = [ValidationError("invalid response"), raw_response]

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(DEVICE_API_CLASS, return_value=api),
        patch(RAW_RESPONSE_TO_DICT, return_value=result) as raw_response_to_dict,
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    assert module.call_api.call_args_list == [
        ((api.get_device_label_sync_provenance, "device-1"),),
        ((api.get_device_label_sync_provenance_without_preload_content, "device-1"),),
    ]
    raw_response_to_dict.assert_called_once_with(raw_response)
    module.exit_json.assert_called_once_with(result=result)


@pytest.mark.parametrize(
    ("params", "message"),
    [
        ({"name": None, "label_keys": None}, "exactly one"),
        ({"name": "", "label_keys": None}, "name must not be empty"),
        ({"name": "device-1", "label_keys": []}, "mutually exclusive"),
        ({"name": None, "label_keys": []}, "between 1 and 50"),
        ({"name": None, "label_keys": ["key"] * 51}, "between 1 and 50"),
        ({"name": None, "label_keys": [""]}, "non-empty strings"),
    ],
)
def test_invalid_provenance_query_fails_before_api_dispatch(params, message):
    module = _mock_module(params)

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(DEVICE_API_CLASS) as device_api,
        patch(LABELSYNCMAPPING_API_CLASS) as labelsyncmapping_api,
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    assert message in module.fail_json.call_args.kwargs["msg"]
    device_api.assert_not_called()
    labelsyncmapping_api.assert_not_called()
    module.call_api.assert_not_called()


def test_both_provenance_query_inputs_are_mutually_exclusive():
    module = _mock_module({"name": "device-1", "label_keys": ["key"]})

    with patch(MODULE_CLASS, return_value=module):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    module.fail_json.assert_called_once_with(
        msg="name and label_keys are mutually exclusive"
    )


@pytest.mark.parametrize(
    "error",
    [
        ApiException(status=404, reason="device not found"),
        ApiException(status=403, reason="forbidden"),
        FlightctlException("connection failed"),
    ],
)
def test_provenance_query_wraps_api_errors(error):
    module = _mock_module({"name": "device-1", "label_keys": None})
    module.call_api.side_effect = error

    with (
        patch(MODULE_CLASS, return_value=module),
        patch(DEVICE_API_CLASS, return_value=MagicMock()),
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    assert (
        "Failed to get label-sync provenance"
        in module.fail_json.call_args.kwargs["msg"]
    )


def test_organization_provenance_query_wraps_api_error():
    module = _mock_module({"name": None, "label_keys": ["example.com/site"]})
    module.call_api.side_effect = ApiException(status=403, reason="forbidden")

    with patch(MODULE_CLASS, return_value=module), patch(
        LABELSYNCMAPPING_API_CLASS, return_value=MagicMock()
    ):
        from plugins.modules.flightctl_label_sync_provenance_info import main

        with pytest.raises(SystemExit):
            main()

    assert "Failed to get label-sync provenance" in module.fail_json.call_args.kwargs[
        "msg"
    ]

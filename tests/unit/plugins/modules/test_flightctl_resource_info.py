from unittest.mock import MagicMock, patch

import pytest

from plugins.modules import flightctl_resource_info


@pytest.mark.parametrize(
    ("selector", "message"),
    [
        ("label_selector", "Label selector is not supported for LabelSyncMapping"),
        ("field_selector", "Field selector is not supported for LabelSyncMapping"),
    ],
)
def test_label_sync_mapping_selector_fails_before_api_dispatch(selector, message):
    module = MagicMock()
    module.params = {
        "kind": "LabelSyncMapping",
        selector: "metadata.name=test",
    }
    module.fail_json.side_effect = SystemExit(1)

    with patch.object(flightctl_resource_info, "FlightctlAPIModule", return_value=module):
        with pytest.raises(SystemExit):
            flightctl_resource_info.main()

    module.fail_json.assert_called_once_with(msg=f"Failed to get resource: {message}")
    module.get_one_or_many.assert_not_called()

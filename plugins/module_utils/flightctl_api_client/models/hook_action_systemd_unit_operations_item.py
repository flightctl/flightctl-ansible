from typing import Literal, Set, cast

HookActionSystemdUnitOperationsItem = Literal[
    "DaemonReload", "Disable", "Enable", "Reload", "Restart", "Start", "Stop"
]

HOOK_ACTION_SYSTEMD_UNIT_OPERATIONS_ITEM_VALUES: Set[
    HookActionSystemdUnitOperationsItem
] = {
    "DaemonReload",
    "Disable",
    "Enable",
    "Reload",
    "Restart",
    "Start",
    "Stop",
}


def check_hook_action_systemd_unit_operations_item(
    value: str,
) -> HookActionSystemdUnitOperationsItem:
    if value in HOOK_ACTION_SYSTEMD_UNIT_OPERATIONS_ITEM_VALUES:
        return cast(HookActionSystemdUnitOperationsItem, value)
    raise TypeError(
        f"Unexpected value {value!r}. Expected one of {HOOK_ACTION_SYSTEMD_UNIT_OPERATIONS_ITEM_VALUES!r}"
    )

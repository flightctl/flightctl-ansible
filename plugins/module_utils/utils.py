#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import copy
import json
import traceback
from typing import Any, Dict, List, Optional, Tuple, Union

from ansible.module_utils.basic import missing_required_lib
from ansible.module_utils.common.dict_transformations import recursive_diff

JSON_PATCH_IMPORT_ERR: Optional[str] = None
try:
    import jsonpatch
    HAS_JSON_PATCH = True
except ImportError:
    HAS_JSON_PATCH = False
    JSON_PATCH_IMPORT_ERR = traceback.format_exc()


def diff_dicts(existing: Dict[str, Any], new: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    Computes the difference between two dictionaries.

    Args:
        existing (Dict[str, Any]): The existing dictionary.
        new (Dict[str, Any]): The new dictionary.

    Returns:
        Tuple[bool, Dict[str, Any]]:
            - A boolean indicating if there are no differences (True) or there are differences (False).
            - A dictionary with the differences, containing 'before' and 'after' states.
    """
    result: Dict[str, Any] = {}

    diff = recursive_diff(existing, new)
    if not diff:
        return True, result

    result["before"] = diff[0]
    result["after"] = diff[1]

    return False, result


def json_patch(existing: Dict[str, Any], patch: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Applies a JSON patch to an existing dictionary.

    Args:
        existing (Dict[str, Any]): The existing dictionary to be patched.
        patch (List[Dict[str, Any]]): The JSON patch to apply.

    Returns:
        Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
            - The patched dictionary if successful, or None if there was an error.
            - An error dictionary if an error occurred, or None if successful.

    Raises:
        ValueError: If there is an error applying the patch or the patch is invalid.
    """
    if not HAS_JSON_PATCH:
        error = {
            "msg": missing_required_lib("jsonpatch"),
            "exception": JSON_PATCH_IMPORT_ERR,
        }
        return None, error
    try:
        _patch = jsonpatch.JsonPatch(patch)
        patched = _patch.apply(existing)
        return patched, None
    except jsonpatch.InvalidJsonPatch as e:
        error = {"msg": "Invalid JSON patch", "exception": e}
        return None, error
    except jsonpatch.JsonPatchConflict as e:
        error = {"msg": "Patch could not be applied due to a conflict", "exception": e}
        return None, error


class JsonPatch(list):
    def __str__(self) -> str:
        """
        Returns a JSON representation of the JsonPatch object.

        Returns:
            str: The JSON string representation of the JsonPatch object.
        """
        return json.dumps(self)


def get_patch(old: Dict[str, Any], new: Dict[str, Any]) -> List[Dict[str, Any]]:
    patch = []

    def recursive_diff(old: Dict[str, Any], new: Dict[str, Any], path: str):
        """
        Recursive function to find differences between old and new dictionaries.
        """
        # for key in old.keys() - new.keys():
        #     patch.append({"op": "remove", "path": f"{path}/{key}"})

        for key in new.keys() - old.keys():
            patch.append({"op": "add", "path": f"{path}/{key}", "value": new[key]})

        for key in old.keys() & new.keys():
            old_value = old[key]
            new_value = new[key]
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                recursive_diff(old_value, new_value, f"{path}/{key}")
            elif old_value != new_value:
                patch.append({"op": "replace", "path": f"{path}/{key}", "value": new_value})

    recursive_diff(old, new, '')

    return patch

#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import ValidationException


def recursive_diff(
    dict1: Dict[str, Any], dict2: Dict[str, Any], position: Optional[Any] = None
):
    if not position:
        if "kind" in dict1 and dict1.get("kind") == dict2.get("kind"):
            position = dict1["kind"]
    left = dict((k, v) for (k, v) in dict1.items() if k not in dict2)
    right = dict((k, v) for (k, v) in dict2.items() if k not in dict1)
    for k in set(dict1.keys()) & set(dict2.keys()):
        if position:
            this_position = "%s.%s" % (position, k)
        if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
            result = recursive_diff(dict1[k], dict2[k], this_position)
            if result:
                left[k] = result[0]
                right[k] = result[1]
        elif isinstance(dict1[k], list) and isinstance(dict2[k], list):
            result = recursive_list_diff(dict1[k], dict2[k], this_position)
            if result:
                left[k] = result[0]
                right[k] = result[1]
        elif dict1[k] != dict2[k]:
            left[k] = dict1[k]
            right[k] = dict2[k]
    if left or right:
        return left, right
    else:
        return None


def list_to_dict(lst: List, key: str, position: str):
    result = OrderedDict()
    for item in lst:
        try:
            result[item[key]] = item
        except KeyError:
            raise ValidationException(
                "Expected key '%s' not found in position %s" % (key, position)
            )
    return result


def recursive_list_diff(list1: List, list2: List, position: Optional[Any] = None):
    result = (list(), list())
    patch_merge_key = position
    dict1 = list_to_dict(list1, patch_merge_key, position)
    dict2 = list_to_dict(list2, patch_merge_key, position)
    dict1_keys = set(dict1.keys())
    dict2_keys = set(dict2.keys())
    for key in dict1_keys - dict2_keys:
        result[0].append(dict1[key])
    for key in dict2_keys - dict1_keys:
        result[1].append(dict2[key])
    for key in dict1_keys & dict2_keys:
        diff = recursive_diff(dict1[key], dict2[key], position)
        if diff:
            # reinsert patch merge key to relate changes in other keys to
            # a specific list element
            diff[0].update({patch_merge_key: dict1[key][patch_merge_key]})
            diff[1].update({patch_merge_key: dict2[key][patch_merge_key]})
            result[0].append(diff[0])
            result[1].append(diff[1])
    if result[0] or result[1]:
        return result
    elif list1 != list2:
        return (list1, list2)
    return None


def diff_objects(existing: Dict[str, Any], new: Dict[str, Any]) -> Tuple[bool, Dict]:
    result = {}

    diff = recursive_diff(existing, new)
    if not diff:
        return True, result

    result["before"] = diff[0]
    result["after"] = diff[1]

    return False, result

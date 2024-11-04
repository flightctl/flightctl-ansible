from __future__ import absolute_import, division, print_function

__metaclass__ = type

from plugins.module_utils.resources import merge_params


def test_merge_params():
    definition = {"kind": "Device"}
    params = {"kind": "Tricycle"}

    merged = merge_params(definition, params)
    assert merged["kind"] == "Device"

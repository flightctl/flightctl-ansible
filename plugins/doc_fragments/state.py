# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  state:
    description:
      - Determines if an object should be created, patched, deleted, or decommissioned.
      - When set to C(present), an object will be created if it does not already exist.
      - If set to C(absent), an existing object will be deleted.
      - If set to C(present), an existing object will be patched if its attributes differ from those specified using I(resource_definition) or I(src).
      - If set to C(decommission), this option is only applicable for the **device** resource type. When set to C(decommission),
        the device will be marked as decommissioned
    choices: ["present", "absent", "decommission"]
    default: "present"
    type: str
  force_update:
    description:
    - If set to C(True), and I(state) is C(present), an existing object will be replaced.
    type: bool
    default: False
"""

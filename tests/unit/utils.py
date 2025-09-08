import json
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    # Clear any existing state first
    basic._ANSIBLE_ARGS = None
    basic._ANSIBLE_PROFILE = None

    # Set up the module arguments in the format expected by current Ansible
    args_json = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args_json)

    # Don't set a profile - let Ansible determine it automatically
    # or try the minimal profile that should exist
    try:
        # This should use the system default serialization
        pass
    except Exception:
        # Fallback: try to avoid the serialization system entirely
        basic._ANSIBLE_PROFILE = None

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

    # Set a basic profile that should be available in most Ansible versions
    basic._ANSIBLE_PROFILE = 'base'

import json
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    # Set arguments in the format expected by Ansible modules
    # Use the original working format from older versions
    basic._ANSIBLE_ARGS = to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': args}))

    # For compatibility with different Ansible versions, try multiple approaches
    # Don't set a profile initially - let Ansible auto-detect
    if hasattr(basic, '_ANSIBLE_PROFILE'):
        basic._ANSIBLE_PROFILE = None

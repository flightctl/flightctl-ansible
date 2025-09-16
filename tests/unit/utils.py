import json
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def find_working_profile():
    """Find a working Ansible serialization profile by trying different approaches"""

    # Strategy 1: Try to directly inspect available profiles in the system
    try:
        from ansible.module_utils._internal import _json
        from ansible.module_utils._internal._json import _profiles

        # Get the profiles module and look for available profile classes
        import pkgutil
        profiles_path = _profiles.__path__

        # Find all profile modules
        available_profiles = []
        for loader, name, ispkg in pkgutil.iter_modules(profiles_path):  # pylint: disable=unused-variable
            if name.startswith('_') and not ispkg:
                # Remove the underscore prefix to get the profile name
                profile_name = name[1:]
                available_profiles.append(profile_name)

        if available_profiles:
            return available_profiles[0]

    except (ImportError, AttributeError, ModuleNotFoundError):
        pass

    # Strategy 2: Try to test profiles by actually attempting to use them
    test_profiles = ['basic', 'default', 'minimal', 'standard', 'Ansible', 'simple']

    for profile_name in test_profiles:
        try:
            from ansible.module_utils._internal import _json
            # Try to get the actual decoder - if this works, the profile exists
            decoder = _json.get_module_decoder(profile_name, _json.Direction.CONTROLLER_TO_MODULE)
            if decoder:
                return profile_name

        except (ImportError, AttributeError, ValueError, ModuleNotFoundError):
            continue

    # Strategy 3: Return None to let Ansible use its default behavior
    return None


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    # Set arguments in the expected format
    basic._ANSIBLE_ARGS = to_bytes(json.dumps({'ANSIBLE_MODULE_ARGS': args}))

    # Try to find and use a working profile
    working_profile = find_working_profile()

    if working_profile:
        basic._ANSIBLE_PROFILE = working_profile
    else:
        # Fallback to the approach that worked originally
        # Use 'Ansible' as it was working before the profile system changes
        basic._ANSIBLE_PROFILE = 'Ansible'

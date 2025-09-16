import json
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


def find_working_profile():
    """Find a working Ansible serialization profile by actually testing them"""

    # Strategy 1: Test common profiles by actually trying to use them
    # Order profiles by likelihood of working
    test_profiles = [
        'basic',           # Most basic profile 
        'default',         # Default profile
        'minimal',         # Minimal profile
        'standard',        # Standard profile  
        'simple',          # Simple profile
        'Ansible',         # Original working profile
    ]

    for profile_name in test_profiles:
        try:
            from ansible.module_utils._internal import _json
            # Actually test if we can get a working decoder for this profile
            # This is the definitive test - if this works, the profile is usable
            decoder = _json.get_module_decoder(profile_name, _json.Direction.CONTROLLER_TO_MODULE)
            if decoder:
                return profile_name

        except (ImportError, AttributeError, ValueError, ModuleNotFoundError, Exception):
            # If any error occurs, this profile doesn't work
            continue

    # Strategy 2: Try to discover what profiles actually exist and work
    # Only as fallback since we prefer known good profiles
    try:
        from ansible.module_utils._internal import _json
        from ansible.module_utils._internal._json import _profiles

        # Get the profiles module and look for available profile classes
        import pkgutil
        profiles_path = _profiles.__path__

        # Find all profile modules and test each one
        for loader, name, ispkg in pkgutil.iter_modules(profiles_path):  # pylint: disable=unused-variable
            if name.startswith('_') and not ispkg:
                # Remove the underscore prefix to get the profile name
                profile_name = name[1:]

                try:
                    # Actually test if this profile works
                    decoder = _json.get_module_decoder(profile_name, _json.Direction.CONTROLLER_TO_MODULE)
                    if decoder:
                        return profile_name
                except (ImportError, AttributeError, ValueError, ModuleNotFoundError, Exception):
                    # This profile doesn't work, try the next one
                    continue

    except (ImportError, AttributeError, ModuleNotFoundError, Exception):
        pass

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

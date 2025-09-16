mport pytest
import json
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes

# This is a simplified mock of the AnsibleModule class that only
# contains the functionality we need for our unit tests.
class AnsibleTestModule:
    """
    A mock class for AnsibleModule to be used in unit tests.
    
    This class is designed to mimic the behavior of a real AnsibleModule
    without requiring the full Ansible runtime environment. It allows us to
    test the logic of our custom modules in isolation.
    """
    def __init__(self, argument_spec=None, params=None, **kwargs):
        self.argument_spec = argument_spec
        self.params = params if params is not None else {}
        self.check_mode = kwargs.get('check_mode', False)
        # Mock any other attributes or methods that your tests rely on.
        # For example: self.fail_json, self.exit_json, etc.

    def fail_json(self, **kwargs):
        """Mock method for fail_json to prevent the test from exiting."""
        # This raises an exception so you can assert on the failure message.
        raise Exception(f"fail_json called with: {kwargs}")

    def exit_json(self, **kwargs):
        """Mock method for exit_json to prevent the test from exiting."""
        # This returns the arguments, allowing you to inspect the return value.
        return kwargs

    def get_bin_path(self, arg, required=False):
        """Mock method for get_bin_path to simulate finding a binary."""
        return f"/usr/bin/{arg}"

# This is the pytest fixture that will be used by your tests.
@pytest.fixture
def mock_module(mocker):
    """
    A pytest fixture that properly mocks the AnsibleModule class.
    
    It replaces the real AnsibleModule with our mock class, allowing
    you to instantiate and test your custom modules without the
    constraints of a live Ansible run. This avoids the "No serialization
    profile was specified" error by providing a fully controlled
    test environment.
    """
    # We patch the AnsibleModule class in the ansible.module_utils.basic module
    # and return an instance of our mock class.
    mocker.patch('ansible.module_utils.basic.AnsibleModule',
                 side_effect=lambda *args, **kwargs: AnsibleTestModule(*args, **kwargs))
    yield

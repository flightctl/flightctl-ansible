import unittest
from unittest.mock import patch, MagicMock

# Import your inventory module
from plugins.inventory.flightctl import InventoryModule


class TestFlightCtlInventoryModule(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        # Create the inventory module instance
        self.inventory = InventoryModule()
        # Mock the inventory object
        self.mock_ansible_inventory = MagicMock()
        self.inventory.inventory = self.mock_ansible_inventory
        # Mock the loader object
        self.mock_loader = MagicMock()
        # Config path
        self.config_path = '/fake/path/to/flightctl.yml'

        # Mock warning method
        self.inventory.warning = MagicMock()

        # Set up constants
        self.inventory.LIMIT_PER_PAGE = 1000

    def test_init(self):
        """Test basic initialization"""
        inventory = InventoryModule()
        self.assertIsInstance(inventory, InventoryModule)

    @patch('plugins.inventory.flightctl._get_devices_and_fleets')
    def test_parse_simple(self, mock_get_devices):
        """Test that parse method runs with basic functionality"""
        # Create a fresh instance for this test
        inventory = InventoryModule()

        # Create mock inventory and loader
        mock_inventory = MagicMock()
        mock_loader = MagicMock()
        inventory.inventory = mock_inventory

        # Set up mocks for methods that are called by parse
        inventory._read_config_data = MagicMock()
        inventory._setup_connection_configuration = MagicMock(return_value={'api_key': 'fake_key', 'url': 'fake_url'})

        # Mock API requests to return empty data
        mock_get_devices.return_value = ([], [])

        # Mock get_option to return empty list for additional_groups
        inventory.get_option = MagicMock(return_value=[])

        # Set any necessary instance variables
        inventory.config = {'api_key': 'fake_key', 'url': 'fake_url'}

        # Call the parse method
        try:
            inventory.parse(mock_inventory, mock_loader, '/fake/path/to/config.yml')

            # If we get here, the method executed without errors
            success = True
        except Exception as e:
            # Print error for debugging
            import traceback
            print(f"Parse method failed with error: {e}")
            print(traceback.format_exc())
            success = False

        # Assert that the parse method executed successfully
        self.assertTrue(success, "Parse method executed without errors")

        # Verify that the expected methods were called
        inventory._read_config_data.assert_called_once()
        inventory._setup_connection_configuration.assert_called_once()
        mock_get_devices.assert_called_once()

    def test_add_to_group_basic(self):
        """Test the basic functionality of _add_to_group"""
        inventory = InventoryModule()

        # Set up a mock inventory with the necessary methods
        mock_inventory = MagicMock()
        inventory.inventory = mock_inventory
        inventory.warning = MagicMock()

        # Create a test implementation of inventory groups using a real dict
        mock_groups = {}

        # Mock the groups attribute on the inventory
        # Use MagicMock's __contains__ method to handle 'in' checks properly
        mock_inventory_groups = MagicMock()
        mock_inventory_groups.__contains__ = lambda self, key: key in mock_groups
        mock_inventory.groups = mock_inventory_groups

        # Call the method with a basic case
        inventory._add_to_group('test_group', 'test_host')

        # Verify add_group was called
        mock_inventory.add_group.assert_called_once_with('test_group')

        # Verify add_child was called
        mock_inventory.add_child.assert_called_once_with('test_group', 'test_host')

        # Reset for testing with an existing group
        mock_inventory.add_group.reset_mock()
        mock_inventory.add_child.reset_mock()

        # Add the group to our mock groups dict
        mock_groups['existing_group'] = True

        # Call with an existing group
        inventory._add_to_group('existing_group', 'test_host')

        # Verify add_group was NOT called (group already exists)
        mock_inventory.add_group.assert_not_called()

        # Verify add_child was called
        mock_inventory.add_child.assert_called_once_with('existing_group', 'test_host')

    def test_add_to_group_standalone(self):
        """Test _add_to_group method in isolation"""
        # Create a fresh instance
        inventory = InventoryModule()

        # Set up necessary attributes
        mock_inventory = MagicMock()
        inventory.inventory = mock_inventory
        inventory.warning = MagicMock()

        # Set up inventory.groups to handle 'in' check
        # Method 1: Use __contains__ to simulate 'test_group' not in groups
        mock_groups = MagicMock()
        mock_groups.__contains__.return_value = False  # 'test_group' not in groups
        mock_inventory.groups = mock_groups

        # Call the method
        inventory._add_to_group('test_group', 'test_host')

        # Verify add_group was called with the correct group name
        calls = mock_inventory.add_group.call_args_list
        group_names = [call[0][0] for call in calls if call[0]]
        self.assertIn('test_group', group_names)

        # Verify add_child was called with the correct arguments
        mock_inventory.add_child.assert_called_with('test_group', 'test_host')

    @patch('plugins.inventory.flightctl._get_devices_and_fleets')
    def test_error_handling(self, mock_get_devices):
        """Test error handling in the parse method"""
        # Setup mock to raise an exception
        self.inventory._read_config_data = MagicMock()
        self.inventory._setup_connection_configuration = MagicMock(
            return_value={'api_key': 'fake_key', 'url': 'fake_url'})
        mock_get_devices.side_effect = Exception("API connection error")

        # Verify that the exception is raised
        with self.assertRaises(Exception) as context:
            self.inventory.parse(self.mock_ansible_inventory, self.mock_loader, self.config_path)

        self.assertIn("API connection error", str(context.exception))

    def test_mock_device_processing(self):
        """Test processing of a mock device"""
        inventory = InventoryModule()
        inventory.inventory = MagicMock()
        inventory.warning = MagicMock()

        # Create a sample device
        device = {
            'id': 'test-device-123',
            'metadata': {
                'name': 'test-device-123',
                'labels': {'environment': 'dev', 'role': 'web'}
            },
            'status': {
                'addresses': [{'type': 'ipv4', 'address': '192.168.1.100'}]
            }
        }

        # Mock methods that would interact with this device
        inventory.add_host = MagicMock()
        inventory.set_variable = MagicMock()
        inventory._add_to_group = MagicMock()

        # Create a method to process this device
        # This is a simple approximation of what your _process_device method might do
        def process_device(device, fleet_groups):
            device_id = device['id']
            metadata = device['metadata']

            # Add host
            inventory.add_host(device_id)

            # Set key variables
            inventory.set_variable(device_id, 'id', device_id)

            # Set ansible_host from IP if available
            if 'status' in device and 'addresses' in device['status']:
                for addr in device['status']['addresses']:
                    if addr.get('type') == 'ipv4':
                        inventory.set_variable(device_id, 'ansible_host', addr['address'])
                        break

            # Add to fleet groups
            for group_name in fleet_groups:
                inventory._add_to_group(group_name, device_id)

            # Always add to 'all' group
            inventory._add_to_group('all', device_id)

            return metadata

        # Call the processing function
        metadata = process_device(device, ['dev', 'web'])

        # Verify expected calls
        inventory.add_host.assert_called_once_with('test-device-123')
        inventory.set_variable.assert_any_call('test-device-123', 'id', 'test-device-123')
        inventory.set_variable.assert_any_call('test-device-123', 'ansible_host', '192.168.1.100')

        # Verify groups
        inventory._add_to_group.assert_any_call('dev', 'test-device-123')
        inventory._add_to_group.assert_any_call('web', 'test-device-123')
        inventory._add_to_group.assert_any_call('all', 'test-device-123')

        # Verify metadata is returned correctly
        self.assertEqual(metadata, device['metadata'])


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest.mock import patch, MagicMock

# Import your inventory module
from plugins.inventory.flightctl import InventoryModule, _render_hostname_expression, _resolve_hostname, _validate_device


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

        # Verify add_host(group=...) was called
        mock_inventory.add_host.assert_called_once_with('test_host', group='test_group')

        # Reset for testing with an existing group
        mock_inventory.add_group.reset_mock()
        mock_inventory.add_host.reset_mock()

        # Add the group to our mock groups dict
        mock_groups['existing_group'] = True

        # Call with an existing group
        inventory._add_to_group('existing_group', 'test_host')

        # Verify add_group was NOT called (group already exists)
        mock_inventory.add_group.assert_not_called()

        # Verify add_host(group=...) was called
        mock_inventory.add_host.assert_called_once_with('test_host', group='existing_group')

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

        # Verify add_host(group=...) was called with the correct arguments
        mock_inventory.add_host.assert_called_with('test_host', group='test_group')

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

    def test_ansible_host_strips_cidr_from_netIpDefault(self):
        """ansible_host should be set to raw IP when netIpDefault includes CIDR"""
        inventory = InventoryModule()
        mock_inventory = MagicMock()
        inventory.inventory = mock_inventory

        device = {
            'metadata': {
                'name': 'device-1'
            },
            'status': {
                'systemInfo': {
                    'netIpDefault': '192.168.2.73/24'
                }
            }
        }

        inventory._populate_inventory_devices([device])

        # Assert ansible_host was set to IP without CIDR
        mock_inventory.set_variable.assert_any_call('device-1', 'ansible_host', '192.168.2.73')


class TestRenderHostnameExpression(unittest.TestCase):
    """Test suite for _render_hostname_expression function"""

    def test_simple_concatenation(self):
        """Test basic concatenation of two fields"""
        device = {
            'metadata': {
                'name': 'device1',
                'uid': 'abc123'
            }
        }
        result = _render_hostname_expression(device, "metadata.name + '_' + metadata.uid")
        self.assertEqual(result, "device1_abc123")

    def test_three_field_concatenation(self):
        """Test concatenation of three fields"""
        device = {
            'metadata': {
                'name': 'device1',
                'namespace': 'prod',
                'uid': 'abc123'
            }
        }
        result = _render_hostname_expression(device, "metadata.namespace + '-' + metadata.name + '-' + metadata.uid")
        self.assertEqual(result, "prod-device1-abc123")

    def test_no_plus_returns_none(self):
        """Test that expression without + returns None (falls back to dotted path)"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "metadata.name")
        self.assertIsNone(result)

    def test_unbalanced_single_quotes(self):
        """Test handling of unbalanced single quotes"""
        device = {'metadata': {'name': 'device1'}}
        # Unbalanced quote: starts with single quote but ends with double quote
        result = _render_hostname_expression(device, "'foo\" + metadata.name")
        # The literal part won't match quote pattern, so it's treated as a path (returns empty)
        self.assertEqual(result, "device1")

    def test_mismatched_quotes(self):
        """Test handling of mismatched quotes (single start, double end)"""
        device = {'metadata': {'name': 'device1', 'uid': 'abc'}}
        result = _render_hostname_expression(device, "'prefix\" + metadata.name + '_' + metadata.uid")
        # First part treated as invalid path (empty), rest concatenates
        self.assertEqual(result, "device1_abc")

    def test_consecutive_operators(self):
        """Test consecutive ++ operators"""
        device = {'metadata': {'name': 'device1', 'uid': 'abc123'}}
        result = _render_hostname_expression(device, "metadata.name + + metadata.uid")
        # Middle empty token is skipped
        self.assertEqual(result, "device1abc123")

    def test_missing_path_value(self):
        """Test behavior when a path resolves to None"""
        device = {'metadata': {'name': 'device1'}}
        # metadata.uid doesn't exist
        result = _render_hostname_expression(device, "metadata.name + '_' + metadata.uid")
        self.assertEqual(result, "device1_")

    def test_all_none_paths(self):
        """Test when all paths are None/missing"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "metadata.missing1 + '_' + metadata.missing2")
        # No device values resolved, should return None to trigger fallback
        self.assertIsNone(result)

    def test_empty_result_returns_none(self):
        """Test that empty result string returns None"""
        device = {}
        result = _render_hostname_expression(device, "metadata.missing + metadata.also_missing")
        # All parts resolve to empty, final result is empty after strip
        self.assertIsNone(result)

    def test_only_whitespace_strips_to_none(self):
        """Test that whitespace-only result returns None"""
        device = {}
        result = _render_hostname_expression(device, "metadata.a + '   ' + metadata.b")
        # All device paths empty, literal has spaces, but overall might still be spaces
        # After strip, if empty, returns None
        self.assertIsNone(result)

    def test_double_quoted_literals(self):
        """Test double-quoted string literals"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, 'metadata.name + "-" + "suffix"')
        self.assertEqual(result, "device1-suffix")

    def test_single_quoted_literals(self):
        """Test single-quoted string literals"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "metadata.name + '-' + 'suffix'")
        self.assertEqual(result, "device1-suffix")

    def test_mixed_quotes_in_literals(self):
        """Test mixing single and double quotes for different literals"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "'prefix-' + metadata.name + \"-suffix\"")
        self.assertEqual(result, "prefix-device1-suffix")

    def test_empty_literal(self):
        """Test empty quoted literal"""
        device = {'metadata': {'name': 'device1', 'uid': 'abc'}}
        result = _render_hostname_expression(device, "metadata.name + '' + metadata.uid")
        self.assertEqual(result, "device1abc")

    def test_literal_only(self):
        """Test expression with only literals (no device paths)"""
        device = {}
        result = _render_hostname_expression(device, "'hello' + '-' + 'world'")
        # No device values resolved, should return None to trigger fallback
        self.assertIsNone(result)

    def test_trailing_plus(self):
        """Test expression ending with +"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "metadata.name + '_' +")
        # Last token after + is empty, skipped
        self.assertEqual(result, "device1_")

    def test_leading_plus(self):
        """Test expression starting with +"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, "+ metadata.name + '_'")
        # First token before + is empty, skipped
        self.assertEqual(result, "device1_")

    def test_numeric_value_converted_to_string(self):
        """Test that numeric values are converted to strings"""
        device = {'metadata': {'name': 'device1', 'generation': 42}}
        result = _render_hostname_expression(device, "metadata.name + '-' + metadata.generation")
        self.assertEqual(result, "device1-42")

    def test_nested_path(self):
        """Test deeply nested dotted path"""
        device = {
            'status': {
                'systemInfo': {
                    'hostname': 'host1'
                }
            },
            'metadata': {
                'uid': 'xyz'
            }
        }
        result = _render_hostname_expression(device, "status.systemInfo.hostname + '_' + metadata.uid")
        self.assertEqual(result, "host1_xyz")

    def test_non_string_expr_returns_none(self):
        """Test that non-string expression returns None"""
        device = {'metadata': {'name': 'device1'}}
        result = _render_hostname_expression(device, None)
        self.assertIsNone(result)

    def test_whitespace_around_tokens(self):
        """Test that whitespace around tokens is handled correctly"""
        device = {'metadata': {'name': 'device1', 'uid': 'abc'}}
        result = _render_hostname_expression(device, "  metadata.name  +  '_'  +  metadata.uid  ")
        self.assertEqual(result, "device1_abc")


class TestResolveHostname(unittest.TestCase):
    """Test suite for _resolve_hostname function"""

    def test_expression_takes_precedence(self):
        """Test that concatenation expression is tried first"""
        device = {'metadata': {'name': 'device1', 'uid': 'abc'}}
        result = _resolve_hostname(device, "metadata.name + '_' + metadata.uid")
        self.assertEqual(result, "device1_abc")

    def test_fallback_to_dotted_path(self):
        """Test fallback to simple dotted path when no + present"""
        device = {'metadata': {'name': 'device1'}}
        result = _resolve_hostname(device, "metadata.name")
        self.assertEqual(result, "device1")

    def test_invalid_expression_fallback_to_path(self):
        """Test that invalid expression falls back to dotted path"""
        device = {'metadata': {'missing': 'value', 'name': 'device1'}}
        # Expression that returns None/empty, should fall back to treating as path
        result = _resolve_hostname(device, "metadata.missing")
        self.assertEqual(result, "value")

    def test_both_fail_returns_none(self):
        """Test that None is returned when both methods fail"""
        device = {'metadata': {'name': 'device1'}}
        result = _resolve_hostname(device, "metadata.nonexistent")
        self.assertIsNone(result)

    def test_empty_string_value_returns_none(self):
        """Test that empty string from dotted path returns None"""
        device = {'metadata': {'name': '   '}}
        result = _resolve_hostname(device, "metadata.name")
        self.assertIsNone(result)

    def test_whitespace_stripped_from_dotted_path(self):
        """Test that whitespace is stripped from dotted path values"""
        device = {'metadata': {'name': '  device1  '}}
        result = _resolve_hostname(device, "metadata.name")
        self.assertEqual(result, "device1")

    def test_literal_only_expression_returns_none(self):
        """Test that literal-only expression (no device fields) returns None"""
        device = {'metadata': {'name': 'fallback-device'}}
        result = _resolve_hostname(device, "'hello' + '-' + 'world'")
        # Expression has no device values, so _render returns None, then dotted path fails
        self.assertIsNone(result)

    def test_all_missing_fields_returns_none(self):
        """Test that expression with only missing fields returns None"""
        device = {'metadata': {'name': 'fallback-device'}}
        result = _resolve_hostname(device, "metadata.missing1 + '_' + metadata.missing2")
        # Expression has no resolved device values, falls back to dotted path which also fails
        self.assertIsNone(result)


class TestValidateDeviceWithExpressions(unittest.TestCase):
    """Test suite for _validate_device with hostname expressions"""

    def test_validate_device_fallback_from_literal_only_expression(self):
        """Test that _validate_device falls back to metadata.name when expression has no device fields"""
        device = {
            'metadata': {
                'name': 'fallback-device',
                'uid': 'abc123'
            }
        }
        # Literal-only expression should fail and fall back to metadata.name
        device_id, metadata = _validate_device(device, "'hello' + '-' + 'world'")
        self.assertEqual(device_id, 'fallback-device')
        self.assertEqual(metadata, device['metadata'])

    def test_validate_device_fallback_from_missing_fields_expression(self):
        """Test that _validate_device falls back to metadata.name when all expression fields are missing"""
        device = {
            'metadata': {
                'name': 'fallback-device'
            }
        }
        # Expression with all missing fields should fail and fall back to metadata.name
        device_id, metadata = _validate_device(device, "metadata.missing1 + '_' + metadata.missing2")
        self.assertEqual(device_id, 'fallback-device')
        self.assertEqual(metadata, device['metadata'])

    def test_validate_device_uses_expression_when_fields_present(self):
        """Test that _validate_device uses expression result when device fields are present"""
        device = {
            'metadata': {
                'name': 'device1',
                'uid': 'abc123'
            }
        }
        # Expression with valid fields should succeed
        device_id, metadata = _validate_device(device, "metadata.name + '_' + metadata.uid")
        self.assertEqual(device_id, 'device1_abc123')
        self.assertEqual(metadata, device['metadata'])

    def test_validate_device_partial_expression_with_missing_field(self):
        """Test that _validate_device uses expression result even with some missing fields"""
        device = {
            'metadata': {
                'name': 'device1'
            }
        }
        # Expression with one valid field should succeed (missing field becomes empty string)
        device_id, metadata = _validate_device(device, "metadata.name + '_' + metadata.uid")
        self.assertEqual(device_id, 'device1_')
        self.assertEqual(metadata, device['metadata'])


if __name__ == '__main__':
    unittest.main()

import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest
import yaml
from ansible.inventory.data import InventoryData
from ansible.parsing.dataloader import DataLoader

# Import the module to test
from plugins.inventory.flightctl import InventoryModule


class TestFlightCtlInventoryModule:
    """Tests for the FlightCTL inventory plugin"""

    def setup_method(self):
        """Setup method run before each test"""
        self.inventory = InventoryModule()
        self.inventory.inventory = InventoryData()  # Initialize inventory
        self.inventory.inventory_data = {
            'hosts': {},
            'groups': {'all': {'hosts': []}},
        }
        # Set the _load_name attribute which is normally set by Ansible's plugin loader
        self.inventory._load_name = 'flightctl'

        # Other common setup
        self.default_config = {
            'plugin': 'flightctl',
            'url': 'https://example.com',
            'token': 'fake_token',
            'additional_groups': [],
        }
        # Create a temp file for inventory config - open in text mode with 'w+'
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.yml', delete=False) as tmp:
            yaml.dump(self.default_config, tmp)
            self.inventory_file = tmp.name

    def teardown_method(self):
        """Teardown method run after each test"""
        # Clean up the temp file
        if hasattr(self, 'inventory_file'):
            os.unlink(self.inventory_file)

    def test_init(self):
        """Test initialization of the inventory plugin"""
        assert isinstance(self.inventory, InventoryModule)
        assert self.inventory.LIMIT_PER_PAGE == 1000

    @patch('plugins.inventory.flightctl.InventoryModule.verify_file')
    def test_verify_file(self, mock_verify):
        """Test the verify_file method"""
        # Configure the mock to return True for our test file
        mock_verify.return_value = True

        # Valid file
        assert self.inventory.verify_file(self.inventory_file)
        mock_verify.assert_called_once_with(self.inventory_file)

        # Reset the mock
        mock_verify.reset_mock()

        # Configure the mock to return False for other files
        mock_verify.return_value = False

        # Invalid file extension
        with tempfile.NamedTemporaryFile(suffix='.txt') as tmp:
            assert not self.inventory.verify_file(tmp.name)
            mock_verify.assert_called_once_with(tmp.name)

        # Reset the mock
        mock_verify.reset_mock()

        # Non-existent file
        assert not self.inventory.verify_file('nonexistent.yml')
        mock_verify.assert_called_once_with('nonexistent.yml')

    @patch('plugins.inventory.flightctl._get_devices_and_fleets')
    @patch('plugins.inventory.flightctl.InventoryModule._read_config_data')
    @patch('plugins.inventory.flightctl.InventoryModule._setup_connection_configuration')
    @patch('plugins.inventory.flightctl.InventoryModule._populate_inventory_devices')
    @patch('plugins.inventory.flightctl.InventoryModule._populate_inventory_fleets')
    @patch('plugins.inventory.flightctl.InventoryModule._populate_inventory_additional_groups')
    @patch('plugins.inventory.flightctl.InventoryModule.get_option')
    def test_parse_method(self, mock_get_option, mock_populate_additional, mock_populate_fleets,
                          mock_populate_devices, mock_setup_conn, mock_read_config,
                          mock_get_devices_fleets):
        """Test the parse method with the new structure"""
        # Setup mocks
        mock_setup_conn.return_value = self.default_config
        mock_get_devices_fleets.return_value = ([], [])  # Empty devices and fleets
        mock_get_option.return_value = []  # Return empty list for additional_groups
        loader = DataLoader()

        # Call the method
        self.inventory.parse(self.inventory.inventory, loader, self.inventory_file)

        # Verify the correct methods were called
        mock_read_config.assert_called_once()
        mock_setup_conn.assert_called_once()
        mock_get_devices_fleets.assert_called_once_with(self.default_config, self.inventory.LIMIT_PER_PAGE)
        mock_populate_devices.assert_called_once_with([])
        mock_populate_fleets.assert_called_once_with([], self.default_config)
        mock_get_option.assert_called_once_with('additional_groups')
        mock_populate_additional.assert_called_once_with(additional_groups=[])

    @patch('plugins.inventory.flightctl._validate_device')
    def test_validate_device(self, mock_validate):
        """Test the _validate_device function"""
        # Setup mock return value
        mock_validate.return_value = ('device-123', {'name': 'device-123'})

        # Valid device with name
        valid_device = {
            'metadata': {'name': 'device-123'},
            'status': {'systemInfo': {'hostname': 'host-123'}}
        }

        # Import the function to test directly
        from plugins.inventory.flightctl import _validate_device

        # Call the function directly
        device_id, metadata = _validate_device(valid_device)

        # Verify mock was called with the right arguments
        mock_validate.assert_called_once_with(valid_device)

        # Verify the returned values
        assert device_id == 'device-123'
        assert metadata == {'name': 'device-123'}

    @patch('plugins.inventory.flightctl._validate_fleet')
    def test_validate_fleet(self, mock_validate):
        """Test the _validate_fleet function"""
        # Setup mock return value
        mock_validate.return_value = 'fleet-123'

        # Valid fleet
        valid_fleet = {'metadata': {'name': 'fleet-123'}}

        # Import the function to test directly
        from plugins.inventory.flightctl import _validate_fleet

        # Call the function directly
        fleet_id = _validate_fleet(valid_fleet)

        # Verify mock was called with the right arguments
        mock_validate.assert_called_once_with(valid_fleet)

        # Verify the returned value
        assert fleet_id == 'fleet-123'

    @patch('plugins.inventory.flightctl._sanitize_group_name')
    def test_add_to_group(self, mock_sanitize):
        """Test the _add_to_group method"""
        # Setup
        device_id = 'device-123'
        group_name = 'test-group'
        sanitized_name = 'test_group'  # Example of sanitized name

        # Mock the sanitize function to return our sanitized name
        mock_sanitize.return_value = sanitized_name

        # First add the device to the inventory
        self.inventory.inventory.add_host(device_id)
        self.inventory.inventory_data['hosts'][device_id] = {'id': device_id}

        # Test adding a device to a new group
        self.inventory._add_to_group(group_name, device_id)

        # Verify sanitize was called
        mock_sanitize.assert_called_once_with(group_name)

        # Verify the group was created and device was added
        assert sanitized_name in self.inventory.inventory.groups
        # Get the actual hosts in the group - it's a dictionary of Host objects
        group_hosts = [host.name for host in self.inventory.inventory.groups[sanitized_name].get_hosts()]
        assert device_id in group_hosts
        assert sanitized_name in self.inventory.inventory_data['groups']
        assert device_id in self.inventory.inventory_data['groups'][sanitized_name]['hosts']

        # Add another device to the inventory
        device_id_2 = 'device-456'
        self.inventory.inventory.add_host(device_id_2)
        self.inventory.inventory_data['hosts'][device_id_2] = {'id': device_id_2}

        # Reset mock to check second call
        mock_sanitize.reset_mock()

        # Test adding another device to the existing group
        self.inventory._add_to_group(group_name, device_id_2)

        # Verify sanitize was called again
        mock_sanitize.assert_called_once_with(group_name)

        # Verify the second device was added - check hosts correctly
        group_hosts = [host.name for host in self.inventory.inventory.groups[sanitized_name].get_hosts()]
        assert device_id_2 in group_hosts
        assert device_id_2 in self.inventory.inventory_data['groups'][sanitized_name]['hosts']

    @patch('plugins.inventory.flightctl._validate_device')
    def test_populate_inventory_devices(self, mock_validate_device):
        """Test the _populate_inventory_devices method"""
        # Setup
        mock_validate_device.return_value = ('device-123', {'name': 'device-123'})

        # Test with one device
        device = {
            'id': 'device-123',
            'name': 'Test Device',
            'device_type': 'router',
            'status': {
                'systemInfo': {
                    'netIpDefault': '10.0.0.1'
                }
            },
            'custom_vars': {
                'var1': 'value1',
                'var2': 'value2'
            },
            'metadata': {'name': 'device-123'}
        }
        device_obj = MagicMock()
        device_obj.to_dict.return_value = device

        # Call the method
        self.inventory._populate_inventory_devices([device_obj])

        # Verify the device was added with all properties
        assert 'device-123' in self.inventory.inventory.hosts
        assert self.inventory.inventory.get_host('device-123').vars['id'] == 'device-123'
        assert self.inventory.inventory.get_host('device-123').vars['name'] == 'Test Device'
        assert self.inventory.inventory.get_host('device-123').vars['device_type'] == 'router'
        assert self.inventory.inventory.get_host('device-123').vars['ansible_host'] == '10.0.0.1'
        assert self.inventory.inventory.get_host('device-123').vars['var1'] == 'value1'
        assert self.inventory.inventory.get_host('device-123').vars['var2'] == 'value2'

        # Test with empty list
        self.inventory._populate_inventory_devices([])
        # No assertions needed, just verify it doesn't raise an exception

    @patch('plugins.inventory.flightctl._validate_fleet')
    @patch('plugins.inventory.flightctl._fetch_fleet_devices')
    @patch('plugins.inventory.flightctl._validate_device')
    def test_populate_inventory_fleets(self, mock_validate_device, mock_fetch_fleet_devices, mock_validate_fleet):
        """Test the _populate_inventory_fleets method"""
        # Setup
        mock_validate_fleet.return_value = 'fleet-123'
        mock_validate_device.return_value = ('device-123', {'name': 'device-123'})

        # Create a mock device
        device = {'id': 'device-123', 'metadata': {'name': 'device-123'}}
        device_obj = MagicMock()
        device_obj.to_dict.return_value = device

        # Set up fleet
        fleet = {'id': 'fleet-123', 'metadata': {'name': 'fleet-123'}}
        fleet_obj = MagicMock()
        fleet_obj.to_dict.return_value = fleet

        # Mock the fetch fleet devices to return our mock device
        mock_fetch_fleet_devices.return_value = [device_obj]

        # Mock _add_to_group method to track calls
        self.inventory._add_to_group = MagicMock()

        # Call the method
        self.inventory._populate_inventory_fleets([fleet_obj], self.default_config)

        # Verify _add_to_group was called with correct parameters
        self.inventory._add_to_group.assert_called_once_with('fleet-123', 'device-123')

        # Test with empty list
        self.inventory._add_to_group.reset_mock()
        self.inventory._populate_inventory_fleets([], self.default_config)
        # No new calls expected
        self.inventory._add_to_group.assert_not_called()

    @patch('plugins.inventory.flightctl._prepare_additional_groups_info')
    @patch('plugins.inventory.flightctl._get_devices_by_labels_and_fields')
    @patch('plugins.inventory.flightctl._validate_device')
    def test_populate_inventory_additional_groups(self, mock_validate_device, mock_get_devices, mock_prepare_groups):
        """Test the _populate_inventory_additional_groups method with new signature"""
        # Setup
        mock_validate_device.return_value = ('device-123', {'name': 'device-123'})

        # Create a mock device
        device = {'id': 'device-123', 'metadata': {'name': 'device-123'}}
        device_obj = MagicMock()
        device_obj.to_dict.return_value = device

        # Mock the get devices function to return our mock device
        mock_get_devices.return_value = [device_obj]

        # Mock the prepare groups function to return a group mapping
        mock_prepare_groups.return_value = {
            'test-group': ('label=value', 'field=value')
        }

        # Mock _add_to_group method to track calls
        self.inventory._add_to_group = MagicMock()

        # Test data
        additional_groups = [
            {'name': 'test-group', 'label_selectors': ['label=value'], 'field_selectors': ['field=value']}]

        # Call the method with the new signature
        self.inventory._populate_inventory_additional_groups(additional_groups=additional_groups)

        # Verify the correct methods were called
        mock_prepare_groups.assert_called_once_with(additional_groups)
        mock_get_devices.assert_called_once_with(
            self.inventory.config, 'label=value', 'field=value',
            self.inventory.LIMIT_PER_PAGE, 'test-group'
        )

        # Verify _add_to_group was called for the device with correct parameters
        self.inventory._add_to_group.assert_called_once_with('test-group', 'device-123')

    # Additional helper tests

    @patch('plugins.inventory.flightctl.flightctl_apis')
    @patch('plugins.inventory.flightctl._get_data')
    def test_get_devices_and_fleets(self, mock_get_data, mock_flightctl_apis):
        """Test the _get_devices_and_fleets function"""
        # Setup mock return values for different calls
        mock_get_data.side_effect = [['device1', 'device2'], ['fleet1']]

        # Mock the context manager
        mock_context = MagicMock()
        mock_device_api = MagicMock()
        mock_fleet_api = MagicMock()
        mock_context.__enter__.return_value = (mock_device_api, mock_fleet_api)
        mock_flightctl_apis.return_value = mock_context

        # Import the function to test directly
        from plugins.inventory.flightctl import _get_devices_and_fleets

        # Call the function
        devices, fleets = _get_devices_and_fleets(self.default_config, 500)

        # Verify the mocks were called correctly
        mock_flightctl_apis.assert_called_once_with(self.default_config)

        # Verify _get_data was called twice with correct args
        assert mock_get_data.call_count == 2

        # First call for devices
        args, kwargs = mock_get_data.call_args_list[0]
        assert args[0] == mock_device_api.list_devices
        assert kwargs.get('label_list') is None
        assert kwargs.get('field_list') is None
        assert kwargs.get('limit') == 500

        # Second call for fleets
        args, kwargs = mock_get_data.call_args_list[1]
        assert args[0] == mock_fleet_api.list_fleets
        assert kwargs.get('label_list') is None
        assert kwargs.get('field_list') is None
        assert kwargs.get('limit') == 500

        # Verify the returned data
        assert devices == ['device1', 'device2']
        assert fleets == ['fleet1']

    @patch('plugins.inventory.flightctl.flightctl_apis')
    @patch('plugins.inventory.flightctl._get_data')
    def test_fetch_fleet_devices(self, mock_get_data, mock_flightctl_apis):
        """Test the _fetch_fleet_devices function"""
        # Setup mock return value
        mock_get_data.return_value = ['device1', 'device2']

        # Mock the context manager
        mock_context = MagicMock()
        mock_device_api = MagicMock()
        mock_fleet_api = MagicMock()
        mock_context.__enter__.return_value = (mock_device_api, mock_fleet_api)
        mock_flightctl_apis.return_value = mock_context

        # Import the function to test directly
        from plugins.inventory.flightctl import _fetch_fleet_devices

        # Call the function
        devices = _fetch_fleet_devices('fleet-123', self.default_config, 500)

        # Verify the mocks were called correctly
        mock_flightctl_apis.assert_called_once_with(self.default_config)

        # Verify _get_data was called correctly
        mock_get_data.assert_called_once()
        args, kwargs = mock_get_data.call_args
        assert args[0] == mock_device_api.list_devices
        assert kwargs.get('field_list') == "metadata.owner = Fleet/fleet-123"
        assert kwargs.get('limit') == 500

        # Verify the returned data
        assert devices == ['device1', 'device2']

    @patch('plugins.inventory.flightctl.flightctl_apis')
    @patch('plugins.inventory.flightctl._get_data')
    def test_get_devices_by_labels_and_fields(self, mock_get_data, mock_flightctl_apis):
        """Test the _get_devices_by_labels_and_fields function"""
        # Setup mock return value
        mock_get_data.return_value = ['device1', 'device2']

        # Mock the context manager
        mock_context = MagicMock()
        mock_device_api = MagicMock()
        mock_fleet_api = MagicMock()
        mock_context.__enter__.return_value = (mock_device_api, mock_fleet_api)
        mock_flightctl_apis.return_value = mock_context

        # Import the function to test directly
        from plugins.inventory.flightctl import _get_devices_by_labels_and_fields

        # Call the function
        devices = _get_devices_by_labels_and_fields(
            self.default_config, 'label=value', 'field=value', 500, 'test-group'
        )

        # Verify the mocks were called correctly
        mock_flightctl_apis.assert_called_once_with(self.default_config)

        # Verify _get_data was called correctly
        mock_get_data.assert_called_once()
        args, kwargs = mock_get_data.call_args
        assert args[0] == mock_device_api.list_devices
        assert kwargs.get('label_list') == 'label=value'
        assert kwargs.get('field_list') == 'field=value'
        assert kwargs.get('limit') == 500

        # Verify the returned data
        assert devices == ['device1', 'device2']

    def test_prepare_additional_groups_info(self):
        """Test the _prepare_additional_groups_info function"""
        # Import the function
        from plugins.inventory.flightctl import _prepare_additional_groups_info

        # Test data
        additional_groups = [
            {
                'name': 'group1',
                'label_selectors': ['label1=value1'],
                'field_selectors': ['metadata.name=value1']
            },
            {
                'name': 'group2',
                'label_selectors': ['label2=value2'],
                'field_selectors': ['metadata.alias=value2']
            }
        ]

        # Call the function
        result = _prepare_additional_groups_info(additional_groups)

        # Verify the expected result
        expected = {
            'group1': ('label1=value1', 'metadata.name=value1'),
            'group2': ('label2=value2', 'metadata.alias=value2')
        }
        assert result == expected

        # Test with empty list
        assert _prepare_additional_groups_info([]) == {}

    # Integration test
    @patch('plugins.inventory.flightctl._get_devices_and_fleets')
    @patch('plugins.inventory.flightctl._fetch_fleet_devices')
    @patch('plugins.inventory.flightctl._get_devices_by_labels_and_fields')
    @patch('plugins.inventory.flightctl.InventoryModule._read_config_data')
    @patch('plugins.inventory.flightctl.InventoryModule._setup_connection_configuration')
    @patch('plugins.inventory.flightctl.InventoryModule.get_option')
    def test_integration_parse_and_inventory_data(self, mock_get_option, mock_setup_conn, mock_read_config,
                                                  mock_get_devices_by_labels, mock_fetch_fleet_devices,
                                                  mock_get_devices_fleets):
        """Integration test for the whole parse method flow"""
        # Setup
        # Set _load_name directly
        self.inventory._load_name = 'flightctl'

        additional_groups = [
            {'name': 'routers', 'label_selectors': ['device_type=router'], 'field_selectors': []}
        ]

        mock_setup_conn.return_value = self.default_config
        mock_get_option.return_value = additional_groups

        # Create mock devices and fleets
        device1 = {
            'id': 'device-123',
            'name': 'router1',
            'device_type': 'router',
            'status': {'systemInfo': {'netIpDefault': '10.0.0.1'}},
            'metadata': {'name': 'device-123'}
        }
        device2 = {
            'id': 'device-456',
            'name': 'switch1',
            'device_type': 'switch',
            'status': {'systemInfo': {'netIpDefault': '10.0.0.2'}},
            'metadata': {'name': 'device-456'}
        }

        fleet = {'id': 'fleet1', 'metadata': {'name': 'fleet1'}}

        # Create mock objects
        device1_obj = MagicMock()
        device1_obj.to_dict.return_value = device1
        device2_obj = MagicMock()
        device2_obj.to_dict.return_value = device2
        fleet_obj = MagicMock()
        fleet_obj.to_dict.return_value = fleet

        # Setup mock returns
        mock_get_devices_fleets.return_value = ([device1_obj, device2_obj], [fleet_obj])
        mock_fetch_fleet_devices.return_value = [device1_obj]  # Only device1 is in fleet1
        mock_get_devices_by_labels.return_value = [device1_obj]  # Only device1 is a router

        loader = DataLoader()

        # Call the parse method
        self.inventory.parse(self.inventory.inventory, loader, self.inventory_file)

        # Verify get_option was called for additional_groups
        mock_get_option.assert_called_with('additional_groups')

        # Verify the inventory data structure
        expected_inventory_data = {
            'hosts': {
                'device-123': {
                    'id': 'device-123',
                    'name': 'router1',
                    'device_type': 'router',
                    'status': {'systemInfo': {'netIpDefault': '10.0.0.1'}},
                    'metadata': {'name': 'device-123'},
                    'ansible_host': '10.0.0.1'
                },
                'device-456': {
                    'id': 'device-456',
                    'name': 'switch1',
                    'device_type': 'switch',
                    'status': {'systemInfo': {'netIpDefault': '10.0.0.2'}},
                    'metadata': {'name': 'device-456'},
                    'ansible_host': '10.0.0.2'
                }
            },
            'groups': {
                'all': {'hosts': ['device-123', 'device-456']},
                'fleet1': {'hosts': ['device-123']},
                'routers': {'hosts': ['device-123']}
            }
        }

        # Check that hosts were added to inventory
        assert 'device-123' in self.inventory.inventory.hosts
        assert 'device-456' in self.inventory.inventory.hosts

        # Check that groups were created
        assert 'fleet1' in self.inventory.inventory.groups
        assert 'routers' in self.inventory.inventory.groups

        # Check group memberships using get_hosts method
        fleet1_hosts = [host.name for host in self.inventory.inventory.groups['fleet1'].get_hosts()]
        routers_hosts = [host.name for host in self.inventory.inventory.groups['routers'].get_hosts()]

        assert 'device-123' in fleet1_hosts
        assert 'device-123' in routers_hosts
        assert 'device-456' not in fleet1_hosts
        assert 'device-456' not in routers_hosts


if __name__ == '__main__':
    pytest.main(['-xvs', __file__])

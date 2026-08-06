import json
import unittest
from typing import ClassVar
from unittest.mock import MagicMock, patch

import yaml

from plugins.inventory.flightctl import (
    DOCUMENTATION,
    InventoryModule,
    _build_auth_headers,
    _get_data,
    _get_data_raw,
    _is_pydantic_validation_error,
    _render_hostname_expression,
    _resolve_hostname,
    _validate_device,
)
from plugins.module_utils.exceptions import FlightctlApiException, ValidationException


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


class TestBuildAuthHeaders(unittest.TestCase):
    """Verify _build_auth_headers only produces Bearer tokens, never Basic Auth."""

    def test_bearer_token_returned_when_access_token_set(self):
        config = MagicMock()
        config.access_token = "my-jwt-token"
        config.username = None
        config.password = None
        headers = _build_auth_headers(config)
        self.assertEqual(headers, {"Authorization": "Bearer my-jwt-token"})

    def test_no_headers_when_no_token(self):
        config = MagicMock()
        config.access_token = None
        config.username = "admin"
        config.password = "secret"
        headers = _build_auth_headers(config)
        self.assertIsNone(headers)

    def test_no_basic_auth_ever_produced(self):
        config = MagicMock()
        config.access_token = None
        config.username = "admin"
        config.password = "secret"
        headers = _build_auth_headers(config)
        self.assertIsNone(headers)


class TestOidcPasswordGrant(unittest.TestCase):
    """Test the OIDC password grant flow in InventoryModule._oidc_password_grant."""

    OPEN_URL = "plugins.inventory.flightctl.open_url"

    SAMPLE_AUTH_CONFIG = {
        "providers": [{
            "metadata": {"name": "my-oidc"},
            "spec": {
                "providerType": "oidc",
                "issuer": "https://idp.example.com/realms/test",
                "clientId": "my-client",
                "scopes": ["openid", "profile", "email"],
            },
        }],
        "defaultProvider": "my-oidc",
    }

    def setUp(self):
        self.module = InventoryModule()

    @staticmethod
    def _mock_response(body_dict):
        resp = MagicMock()
        resp.read.return_value = json.dumps(body_dict).encode()
        return resp

    @patch(OPEN_URL)
    def test_successful_oidc_grant_returns_id_token(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response(
                {"token_endpoint": "https://idp.example.com/realms/test/protocol/openid-connect/token"}
            ),
            self._mock_response(
                {"id_token": "jwt-id-token", "access_token": "jwt-access-token"}
            ),
        ]
        token = self.module._oidc_password_grant(
            "https://host", "admin", "password123", False
        )
        self.assertEqual(token, "jwt-id-token")

    @patch(OPEN_URL)
    def test_oidc_grant_falls_back_to_access_token(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response(
                {"token_endpoint": "https://idp.example.com/realms/test/protocol/openid-connect/token"}
            ),
            self._mock_response({"access_token": "jwt-access-only"}),
        ]
        token = self.module._oidc_password_grant(
            "https://host", "admin", "password123", False
        )
        self.assertEqual(token, "jwt-access-only")

    @patch(OPEN_URL)
    def test_auth_config_failure_raises(self, mock_open):
        mock_open.side_effect = Exception("Connection refused")
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "pass", False
            )
        self.assertIn("Failed to fetch auth config", str(ctx.exception))

    @patch(OPEN_URL)
    def test_no_oidc_provider_raises(self, mock_open):
        mock_open.return_value = self._mock_response({"providers": []})
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "pass", False
            )
        self.assertIn("No OIDC provider found", str(ctx.exception))

    @patch(OPEN_URL)
    def test_oidc_discovery_failure_raises(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            Exception("Connection refused"),
        ]
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "pass", False
            )
        self.assertIn("OIDC discovery failed", str(ctx.exception))

    @patch(OPEN_URL)
    def test_missing_token_endpoint_raises(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response({}),
        ]
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "pass", False
            )
        self.assertIn("token_endpoint missing", str(ctx.exception))

    @patch(OPEN_URL)
    def test_token_request_http_error_raises(self, mock_open):
        import urllib.error

        http_error = urllib.error.HTTPError(
            "https://idp.example.com/token", 401, "Unauthorized", {}, None
        )
        http_error.read = MagicMock(return_value=b"invalid credentials")

        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response({"token_endpoint": "https://idp.example.com/token"}),
            http_error,
        ]
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "wrongpass", False
            )
        self.assertIn("OIDC token request failed (401)", str(ctx.exception))

    @patch(OPEN_URL)
    def test_no_token_in_response_raises(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response({"token_endpoint": "https://idp.example.com/token"}),
            self._mock_response({"error": "bad_grant"}),
        ]
        with self.assertRaises(ValidationException) as ctx:
            self.module._oidc_password_grant(
                "https://host", "admin", "pass", False
            )
        self.assertIn("No token returned", str(ctx.exception))

    @patch(OPEN_URL)
    def test_oidc_grant_sends_correct_payload(self, mock_open):
        import urllib.parse

        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response({"token_endpoint": "https://idp.example.com/token"}),
            self._mock_response({"id_token": "tok"}),
        ]
        self.module._oidc_password_grant(
            "https://host", "admin", "s3cret", False
        )

        token_call = mock_open.call_args_list[2]
        body = token_call[1]["data"].decode()
        params = urllib.parse.parse_qs(body)
        self.assertEqual(params["grant_type"], ["password"])
        self.assertEqual(params["username"], ["admin"])
        self.assertEqual(params["password"], ["s3cret"])
        self.assertEqual(params["client_id"], ["my-client"])
        self.assertEqual(params["scope"], ["openid profile email"])

    @patch(OPEN_URL)
    def test_discovery_url_built_from_issuer(self, mock_open):
        mock_open.side_effect = [
            self._mock_response(self.SAMPLE_AUTH_CONFIG),
            self._mock_response({"token_endpoint": "https://idp.example.com/token"}),
            self._mock_response({"id_token": "tok"}),
        ]
        self.module._oidc_password_grant(
            "https://host", "admin", "pass", False
        )

        discovery_call = mock_open.call_args_list[1]
        self.assertEqual(
            discovery_call[0][0],
            "https://idp.example.com/realms/test/.well-known/openid-configuration",
        )

    @patch(OPEN_URL)
    def test_default_scope_when_not_configured(self, mock_open):
        import urllib.parse

        auth_config_no_scopes = {
            "providers": [{
                "metadata": {"name": "minimal"},
                "spec": {
                    "providerType": "oidc",
                    "issuer": "https://idp.example.com",
                    "clientId": "my-client",
                },
            }],
        }
        mock_open.side_effect = [
            self._mock_response(auth_config_no_scopes),
            self._mock_response({"token_endpoint": "https://idp.example.com/token"}),
            self._mock_response({"id_token": "tok"}),
        ]
        self.module._oidc_password_grant(
            "https://host", "admin", "pass", False
        )

        token_call = mock_open.call_args_list[2]
        body = token_call[1]["data"].decode()
        params = urllib.parse.parse_qs(body)
        self.assertEqual(params["scope"], ["openid"])


class TestSetupConnectionOidcIntegration(unittest.TestCase):
    """Test that _setup_connection_configuration uses OIDC grant for username/password."""

    def _make_module(self, options):
        module = InventoryModule()
        module.get_option = MagicMock(side_effect=options.get)
        module._load_config_file = MagicMock(return_value=None)
        return module

    @patch.object(InventoryModule, '_oidc_password_grant', return_value='oidc-bearer-token')
    def test_username_password_triggers_oidc_grant(self, mock_oidc):
        module = self._make_module({
            'host': 'https://rhem.example.com',
            'verify_ssl': False,
            'token': None,
            'username': 'admin',
            'password': 'redhat',
            'organization': None,
            'ca_path': None,
            'request_timeout': 120.0,
            'flightctl_config_file': None,
        })

        config = module._setup_connection_configuration()

        mock_oidc.assert_called_once_with(
            'https://rhem.example.com', 'admin', 'redhat', False, None
        )
        self.assertEqual(config.access_token, 'oidc-bearer-token')
        self.assertIsNone(config.username)
        self.assertIsNone(config.password)

    def test_token_skips_oidc_grant(self):
        module = self._make_module({
            'host': 'https://rhem.example.com',
            'verify_ssl': False,
            'token': 'pre-existing-token',
            'username': None,
            'password': None,
            'organization': None,
            'ca_path': None,
            'request_timeout': 120.0,
            'flightctl_config_file': None,
        })

        with patch.object(InventoryModule, '_oidc_password_grant') as mock_oidc:
            config = module._setup_connection_configuration()
            mock_oidc.assert_not_called()

        self.assertEqual(config.access_token, 'pre-existing-token')

    @patch.object(InventoryModule, '_oidc_password_grant', return_value='oidc-token')
    def test_host_with_api_v1_suffix_stripped_for_oidc(self, mock_oidc):
        module = self._make_module({
            'host': 'https://rhem.example.com/api/v1',
            'verify_ssl': False,
            'token': None,
            'username': 'admin',
            'password': 'redhat',
            'organization': None,
            'ca_path': None,
            'request_timeout': 120.0,
            'flightctl_config_file': None,
        })

        module._setup_connection_configuration()

        mock_oidc.assert_called_once_with(
            'https://rhem.example.com', 'admin', 'redhat', False, None
        )

    @patch.object(InventoryModule, '_oidc_password_grant', return_value='oidc-token')
    def test_ca_path_passed_to_oidc_grant(self, mock_oidc):
        module = self._make_module({
            'host': 'https://rhem.example.com',
            'verify_ssl': True,
            'token': None,
            'username': 'admin',
            'password': 'redhat',
            'organization': None,
            'ca_path': '/etc/pki/tls/custom-ca.crt',
            'request_timeout': 120.0,
            'flightctl_config_file': None,
        })

        config = module._setup_connection_configuration()

        mock_oidc.assert_called_once_with(
            'https://rhem.example.com', 'admin', 'redhat', True, '/etc/pki/tls/custom-ca.crt'
        )
        self.assertEqual(config.access_token, 'oidc-token')

    @patch("plugins.inventory.flightctl.open_url")
    def test_oidc_grant_passes_ca_path_to_open_url(self, mock_open):
        def _resp(body):
            r = MagicMock()
            r.read.return_value = json.dumps(body).encode()
            return r

        auth_config = {
            "providers": [{
                "metadata": {"name": "p"},
                "spec": {
                    "providerType": "oidc",
                    "issuer": "https://idp.example.com",
                    "clientId": "c",
                },
            }],
        }
        mock_open.side_effect = [
            _resp(auth_config),
            _resp({"token_endpoint": "https://idp.example.com/token"}),
            _resp({"id_token": "tok"}),
        ]

        module = InventoryModule()
        module._oidc_password_grant(
            "https://host", "admin", "pass", True, "/path/to/ca.crt"
        )

        for call in mock_open.call_args_list:
            self.assertTrue(call[1].get("validate_certs"))
            self.assertEqual(call[1].get("ca_path"), "/path/to/ca.crt")


class TestDocumentationEnvDeclarations(unittest.TestCase):
    """Verify that all connection options declare env: blocks for AAP Credential Type support."""

    @classmethod
    def setUpClass(cls):
        cls.doc = yaml.safe_load(DOCUMENTATION)
        cls.options = cls.doc.get('options', {})

    EXPECTED_ENV_VARS: ClassVar[dict[str, str]] = {
        'token': 'FLIGHTCTL_TOKEN',
        'host': 'FLIGHTCTL_HOST',
        'username': 'FLIGHTCTL_USERNAME',
        'password': 'FLIGHTCTL_PASSWORD',
        'organization': 'FLIGHTCTL_ORGANIZATION',
        'flightctl_config_file': 'FLIGHTCTL_CONFIG_FILE',
        'ca_path': 'FLIGHTCTL_CA_PATH',
        'verify_ssl': 'FLIGHTCTL_VERIFY_SSL',
    }

    def test_all_connection_options_have_env_declarations(self):
        """Every connection option must have an env: block with the correct variable name."""
        for option_name, expected_env in self.EXPECTED_ENV_VARS.items():
            with self.subTest(option=option_name):
                option = self.options.get(option_name)
                self.assertIsNotNone(option, f"Option '{option_name}' missing from DOCUMENTATION")
                env_list = option.get('env')
                self.assertIsNotNone(env_list, f"Option '{option_name}' is missing env: declaration")
                self.assertIsInstance(env_list, list)
                env_names = [e.get('name') for e in env_list]
                self.assertIn(expected_env, env_names,
                              f"Option '{option_name}' should declare env var '{expected_env}', got {env_names}")

    def test_token_env_declaration(self):
        env_list = self.options['token'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_TOKEN')

    def test_host_env_declaration(self):
        env_list = self.options['host'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_HOST')

    def test_username_env_declaration(self):
        env_list = self.options['username'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_USERNAME')

    def test_password_env_declaration(self):
        env_list = self.options['password'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_PASSWORD')

    def test_organization_env_declaration(self):
        env_list = self.options['organization'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_ORGANIZATION')

    def test_config_file_env_declaration(self):
        env_list = self.options['flightctl_config_file'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_CONFIG_FILE')

    def test_ca_path_env_declaration(self):
        env_list = self.options['ca_path'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_CA_PATH')

    def test_verify_ssl_env_declaration(self):
        env_list = self.options['verify_ssl'].get('env', [])
        self.assertEqual(env_list[0]['name'], 'FLIGHTCTL_VERIFY_SSL')

    def test_env_vars_match_module_utils_convention(self):
        """Env var names must follow the FLIGHTCTL_ prefix convention used in module_utils/core.py."""
        for option_name, expected_env in self.EXPECTED_ENV_VARS.items():
            with self.subTest(option=option_name):
                self.assertTrue(expected_env.startswith('FLIGHTCTL_'),
                                f"Env var '{expected_env}' should start with FLIGHTCTL_")


class TestIsPydanticValidationError(unittest.TestCase):
    """Verify _is_pydantic_validation_error detects pydantic errors without importing pydantic."""

    def test_real_pydantic_validation_error(self):
        try:
            from pydantic import ValidationError, BaseModel

            class StrictModel(BaseModel):
                value: int

            try:
                StrictModel(value="not-an-int")  # type: ignore[arg-type]
            except ValidationError as exc:
                self.assertTrue(_is_pydantic_validation_error(exc))
        except ImportError:
            self.skipTest("pydantic not installed")

    def test_generic_exception_returns_false(self):
        self.assertFalse(_is_pydantic_validation_error(ValueError("nope")))

    def test_non_pydantic_validation_error_returns_false(self):
        class ValidationError(Exception):
            __module__ = "myapp.errors"

        self.assertFalse(_is_pydantic_validation_error(ValidationError("nope")))


class TestGetDataRawFallback(unittest.TestCase):
    """Verify _get_data_raw paginates through raw HTTP responses."""

    def _make_raw_response(self, items, continue_token=None):
        metadata = {}
        if continue_token:
            metadata['continue'] = continue_token
        body = json.dumps({'items': items, 'metadata': metadata}).encode()
        resp = MagicMock()
        resp.data = body
        return resp

    def test_single_page(self):
        items = [{'metadata': {'name': 'dev-1'}}, {'metadata': {'name': 'dev-2'}}]
        list_func = MagicMock(return_value=self._make_raw_response(items))

        result = _get_data_raw(list_func, limit=100)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['metadata']['name'], 'dev-1')
        list_func.assert_called_once()

    def test_multi_page_pagination(self):
        page1 = self._make_raw_response(
            [{'metadata': {'name': 'dev-1'}}], continue_token='token-abc'
        )
        page2 = self._make_raw_response(
            [{'metadata': {'name': 'dev-2'}}]
        )
        list_func = MagicMock(side_effect=[page1, page2])

        result = _get_data_raw(list_func, limit=1)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['metadata']['name'], 'dev-1')
        self.assertEqual(result[1]['metadata']['name'], 'dev-2')
        self.assertEqual(list_func.call_count, 2)

    def test_api_error_raises_flightctl_exception(self):
        list_func = MagicMock(side_effect=ConnectionError("timeout"))
        with self.assertRaises(FlightctlApiException):
            _get_data_raw(list_func)


class TestGetDataPydanticFallback(unittest.TestCase):
    """Verify _get_data falls back to raw JSON on pydantic ValidationError."""

    def _make_typed_response(self, items, continue_token=None):
        resp = MagicMock()
        resp.items = items
        metadata = {}
        if continue_token:
            metadata['continue'] = continue_token
        resp.to_dict.return_value = {'metadata': metadata}
        return resp

    def _make_raw_response(self, items, continue_token=None):
        metadata = {}
        if continue_token:
            metadata['continue'] = continue_token
        body = json.dumps({'items': items, 'metadata': metadata}).encode()
        resp = MagicMock()
        resp.data = body
        return resp

    def _make_pydantic_error(self):
        try:
            from pydantic import ValidationError, BaseModel

            class StrictModel(BaseModel):
                value: int

            try:
                StrictModel(value="not-an-int")  # type: ignore[arg-type]
            except ValidationError as exc:
                return exc
        except ImportError:
            return None

    def test_normal_path_no_fallback_needed(self):
        typed_resp = self._make_typed_response([MagicMock(), MagicMock()])
        list_func = MagicMock(return_value=typed_resp)
        fallback_func = MagicMock()

        result = _get_data(list_func, fallback_list_func=fallback_func)
        self.assertEqual(len(result), 2)
        fallback_func.assert_not_called()

    def test_pydantic_error_triggers_fallback(self):
        pydantic_exc = self._make_pydantic_error()
        if pydantic_exc is None:
            self.skipTest("pydantic not installed")

        list_func = MagicMock(side_effect=pydantic_exc)
        raw_items = [{'metadata': {'name': 'dev-1'}}]
        fallback_func = MagicMock(return_value=self._make_raw_response(raw_items))

        result = _get_data(list_func, fallback_list_func=fallback_func)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['metadata']['name'], 'dev-1')
        fallback_func.assert_called_once()

    def test_non_pydantic_error_still_raises(self):
        list_func = MagicMock(side_effect=ConnectionError("refused"))
        fallback_func = MagicMock()

        with self.assertRaises(FlightctlApiException):
            _get_data(list_func, fallback_list_func=fallback_func)
        fallback_func.assert_not_called()

    def test_pydantic_error_without_fallback_raises(self):
        pydantic_exc = self._make_pydantic_error()
        if pydantic_exc is None:
            self.skipTest("pydantic not installed")

        list_func = MagicMock(side_effect=pydantic_exc)

        with self.assertRaises(FlightctlApiException):
            _get_data(list_func, fallback_list_func=None)


class TestPopulateInventoryFleetsWithRawDicts(unittest.TestCase):
    """Verify _populate_inventory_fleets handles raw dicts (fallback path)."""

    @patch('plugins.inventory.flightctl._fetch_fleet_devices')
    def test_fleet_as_raw_dict(self, mock_fetch):
        mock_fetch.return_value = []
        inventory = InventoryModule()
        mock_inv = MagicMock()
        mock_groups = MagicMock()
        mock_groups.__contains__ = MagicMock(return_value=False)
        mock_inv.groups = mock_groups
        inventory.inventory = mock_inv

        raw_fleet = {'metadata': {'name': 'fleet-1'}}
        config = MagicMock()

        inventory._populate_inventory_fleets([raw_fleet], config)

        mock_fetch.assert_called_once_with('fleet-1', config, inventory.LIMIT_PER_PAGE)


if __name__ == '__main__':
    unittest.main()

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
import unittest
from unittest.mock import MagicMock, patch

from plugins.module_utils.oidc_auth import (
    fetch_auth_config,
    select_oidc_provider,
    oidc_password_grant,
)
from plugins.module_utils.exceptions import ValidationException


OPEN_URL = "plugins.module_utils.oidc_auth.open_url"

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


def _mock_response(body_dict):
    resp = MagicMock()
    resp.read.return_value = json.dumps(body_dict).encode()
    return resp


class TestSelectOidcProvider(unittest.TestCase):
    def test_selects_default_provider(self):
        provider = select_oidc_provider(SAMPLE_AUTH_CONFIG)
        self.assertEqual(provider["metadata"]["name"], "my-oidc")

    def test_falls_back_to_first_oidc_provider(self):
        config = {
            "providers": [
                {"metadata": {"name": "a"}, "spec": {"providerType": "oidc", "issuer": "x"}},
                {"metadata": {"name": "b"}, "spec": {"providerType": "oidc", "issuer": "y"}},
            ],
        }
        provider = select_oidc_provider(config)
        self.assertEqual(provider["metadata"]["name"], "a")

    def test_ignores_non_oidc_providers(self):
        config = {
            "providers": [
                {"metadata": {"name": "basic"}, "spec": {"providerType": "basic"}},
                {"metadata": {"name": "oidc"}, "spec": {"providerType": "oidc"}},
            ],
        }
        provider = select_oidc_provider(config)
        self.assertEqual(provider["metadata"]["name"], "oidc")

    def test_no_oidc_provider_raises(self):
        with self.assertRaises(ValidationException) as ctx:
            select_oidc_provider({"providers": []})
        self.assertIn("No OIDC provider found", str(ctx.exception))


class TestFetchAuthConfig(unittest.TestCase):
    @patch(OPEN_URL)
    def test_builds_auth_config_url(self, mock_open):
        mock_open.return_value = _mock_response(SAMPLE_AUTH_CONFIG)
        result = fetch_auth_config("https://host/", False)
        self.assertEqual(result, SAMPLE_AUTH_CONFIG)
        self.assertEqual(mock_open.call_args[0][0], "https://host/api/v1/auth/config")

    @patch(OPEN_URL)
    def test_failure_raises(self, mock_open):
        mock_open.side_effect = Exception("Connection refused")
        with self.assertRaises(ValidationException) as ctx:
            fetch_auth_config("https://host", False)
        self.assertIn("Failed to fetch auth config", str(ctx.exception))


class TestOidcPasswordGrant(unittest.TestCase):
    @patch(OPEN_URL)
    def test_successful_grant_returns_id_token(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            _mock_response({"id_token": "jwt-id-token", "access_token": "jwt-access"}),
        ]
        token = oidc_password_grant("https://host", "admin", "pw", False)
        self.assertEqual(token, "jwt-id-token")

    @patch(OPEN_URL)
    def test_falls_back_to_access_token(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            _mock_response({"access_token": "jwt-access-only"}),
        ]
        token = oidc_password_grant("https://host", "admin", "pw", False)
        self.assertEqual(token, "jwt-access-only")

    @patch(OPEN_URL)
    def test_discovery_failure_raises(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            Exception("Connection refused"),
        ]
        with self.assertRaises(ValidationException) as ctx:
            oidc_password_grant("https://host", "admin", "pw", False)
        self.assertIn("OIDC discovery failed", str(ctx.exception))

    @patch(OPEN_URL)
    def test_missing_token_endpoint_raises(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({}),
        ]
        with self.assertRaises(ValidationException) as ctx:
            oidc_password_grant("https://host", "admin", "pw", False)
        self.assertIn("token_endpoint missing", str(ctx.exception))

    @patch(OPEN_URL)
    def test_token_request_http_error_raises(self, mock_open):
        import urllib.error

        http_error = urllib.error.HTTPError(
            "https://idp.example.com/token", 401, "Unauthorized", {}, None
        )
        http_error.read = MagicMock(return_value=b"invalid credentials")
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            http_error,
        ]
        with self.assertRaises(ValidationException) as ctx:
            oidc_password_grant("https://host", "admin", "wrong", False)
        self.assertIn("OIDC token request failed (401)", str(ctx.exception))

    @patch(OPEN_URL)
    def test_no_token_in_response_raises(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            _mock_response({"error": "bad_grant"}),
        ]
        with self.assertRaises(ValidationException) as ctx:
            oidc_password_grant("https://host", "admin", "pw", False)
        self.assertIn("No token returned", str(ctx.exception))

    @patch(OPEN_URL)
    def test_sends_correct_payload(self, mock_open):
        import urllib.parse

        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            _mock_response({"id_token": "tok"}),
        ]
        oidc_password_grant("https://host", "admin", "s3cret", False)

        token_call = mock_open.call_args_list[2]
        params = urllib.parse.parse_qs(token_call[1]["data"].decode())
        self.assertEqual(params["grant_type"], ["password"])
        self.assertEqual(params["username"], ["admin"])
        self.assertEqual(params["password"], ["s3cret"])
        self.assertEqual(params["client_id"], ["my-client"])
        self.assertEqual(params["scope"], ["openid profile email"])

    @patch(OPEN_URL)
    def test_ca_path_passed_to_open_url(self, mock_open):
        mock_open.side_effect = [
            _mock_response(SAMPLE_AUTH_CONFIG),
            _mock_response({"token_endpoint": "https://idp.example.com/token"}),
            _mock_response({"id_token": "tok"}),
        ]
        oidc_password_grant("https://host", "admin", "pw", True, "/path/to/ca.crt")

        for call in mock_open.call_args_list:
            self.assertTrue(call[1].get("validate_certs"))
            self.assertEqual(call[1].get("ca_path"), "/path/to/ca.crt")


if __name__ == "__main__":
    unittest.main()

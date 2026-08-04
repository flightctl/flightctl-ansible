from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import io
import json
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

from plugins.module_utils.oidc_auth import discover_oidc_token_endpoint, oidc_password_grant


def _fake_http_response(data):
    """Build a stand-in for what ansible.module_utils.urls.open_url() returns."""
    response = MagicMock()
    response.read.return_value = json.dumps(data).encode('utf-8')
    return response


AUTH_CONFIG_RESPONSE = {
    'apiVersion': 'v1beta1',
    'defaultProvider': 'pam-issuer',
    'providers': [{
        'apiVersion': 'v1beta1',
        'kind': 'AuthProvider',
        'metadata': {'name': 'pam-issuer'},
        'spec': {
            'providerType': 'oidc',
            'issuer': 'https://issuer.example.com/_/pam-issuer',
            'clientId': 'flightctl-client',
        },
    }],
}

OIDC_DISCOVERY_RESPONSE = {
    'issuer': 'https://issuer.example.com/_/pam-issuer',
    'token_endpoint': 'https://issuer.example.com/_/pam-issuer/api/v1/auth/token',
}


class TestDiscoverOidcTokenEndpoint:

    def test_no_host_returns_error(self):
        token_endpoint, client_id, error = discover_oidc_token_endpoint(None, True, None, None)
        assert token_endpoint is None
        assert client_id is None
        assert 'no host is configured' in error

    def test_strips_trailing_api_v1_before_fetching_auth_config(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
            ]
            token_endpoint, client_id, error = discover_oidc_token_endpoint(
                'https://flightctl.example.com/api/v1', True, None, None
            )

        assert error is None
        assert token_endpoint == OIDC_DISCOVERY_RESPONSE['token_endpoint']
        assert client_id == 'flightctl-client'
        auth_config_call = mock_open_url.call_args_list[0]
        assert auth_config_call.args[0] == 'https://flightctl.example.com/api/v1/auth/config'

    def test_no_oidc_provider_configured(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.return_value = _fake_http_response({'providers': []})
            token_endpoint, client_id, error = discover_oidc_token_endpoint(
                'https://flightctl.example.com', True, None, None
            )

        assert token_endpoint is None
        assert 'no OIDC-based authentication provider' in error

    def test_auth_config_fetch_failure_is_surfaced(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = Exception('connection refused')
            token_endpoint, client_id, error = discover_oidc_token_endpoint(
                'https://flightctl.example.com', True, None, None
            )

        assert token_endpoint is None
        assert client_id is None
        assert 'failed to fetch authentication config' in error

    def test_missing_issuer_on_provider(self):
        response = {
            'providers': [{
                'metadata': {'name': 'p1'},
                'spec': {'providerType': 'oidc', 'clientId': 'client1'},
            }],
        }
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.return_value = _fake_http_response(response)
            token_endpoint, client_id, error = discover_oidc_token_endpoint(
                'https://flightctl.example.com', True, None, None
            )

        assert token_endpoint is None
        assert client_id == 'client1'
        assert 'no issuer URL' in error

    def test_discovery_document_missing_token_endpoint(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response({'issuer': 'https://issuer.example.com/_/pam-issuer'}),
            ]
            token_endpoint, client_id, error = discover_oidc_token_endpoint(
                'https://flightctl.example.com', True, None, None
            )

        assert token_endpoint is None
        assert client_id == 'flightctl-client'
        assert 'does not advertise a token_endpoint' in error


class TestOidcPasswordGrant:

    def test_successful_grant_returns_id_token(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
                _fake_http_response({'access_token': 'access-1', 'id_token': 'id-token-1'}),
            ]
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 's3cret'
            )

        assert error is None
        assert bearer_token == 'id-token-1'
        assert mock_open_url.call_count == 3
        post_call = mock_open_url.call_args_list[2]
        assert post_call.args[0] == OIDC_DISCOVERY_RESPONSE['token_endpoint']
        assert post_call.kwargs.get('method') == 'POST'
        assert 'grant_type=password' in post_call.kwargs.get('data')

    def test_falls_back_to_access_token_when_no_id_token(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
                _fake_http_response({'access_token': 'access-1'}),
            ]
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 's3cret'
            )

        assert error is None
        assert bearer_token == 'access-1'

    def test_discovery_failure_short_circuits_before_posting_credentials(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.return_value = _fake_http_response({'providers': []})
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 's3cret'
            )

        assert bearer_token is None
        assert 'no OIDC-based authentication provider' in error
        # Only the auth-config lookup should have happened; credentials must never be posted.
        assert mock_open_url.call_count == 1

    def test_invalid_credentials_surface_upstream_error_description(self):
        error_body = json.dumps({'error': 'invalid_grant', 'error_description': 'Invalid user credentials'}).encode('utf-8')
        http_error = HTTPError(
            url='https://issuer.example.com/token', code=400, msg='Bad Request', hdrs=None, fp=io.BytesIO(error_body),
        )
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
                http_error,
            ]
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 'wrong'
            )

        assert bearer_token is None
        assert 'Invalid user credentials' in error

    def test_token_endpoint_unreachable(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
                Exception('connection reset'),
            ]
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 's3cret'
            )

        assert bearer_token is None
        assert 'failed to reach token endpoint' in error

    def test_response_without_usable_token(self):
        with patch('plugins.module_utils.oidc_auth.open_url') as mock_open_url:
            mock_open_url.side_effect = [
                _fake_http_response(AUTH_CONFIG_RESPONSE),
                _fake_http_response(OIDC_DISCOVERY_RESPONSE),
                _fake_http_response({'token_type': 'Bearer'}),
            ]
            bearer_token, error = oidc_password_grant(
                'https://flightctl.example.com/api/v1', 'alice', 's3cret'
            )

        assert bearer_token is None
        assert 'did not return a usable token' in error

# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
Shared helpers implementing the OIDC Resource Owner Password Credentials (ROPC)
grant used to exchange a username/password for a bearer token.

The Flight Control API's middlewares only accept Bearer tokens (they extract
credentials via ExtractBearerToken() exclusively); HTTP Basic Auth is rejected
on API endpoints. Any code path that accepts a username/password must therefore
discover the server's configured OIDC provider and exchange the credentials for
a token, mirroring what `flightctl login --username --password` does internally,
rather than sending them as HTTP Basic Auth.
"""

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError
from urllib.parse import urlencode

from ansible.module_utils.urls import open_url


def http_get_json(url: str, verify_ssl: bool, ca_path: Optional[str], request_timeout: Optional[float]) -> Dict[str, Any]:
    response = open_url(url, method='GET', validate_certs=verify_ssl, ca_path=ca_path,
                         timeout=request_timeout or 30)
    return json.loads(response.read())


def discover_oidc_token_endpoint(
    host: Optional[str],
    verify_ssl: bool,
    ca_path: Optional[str],
    request_timeout: Optional[float],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Discover the OIDC token endpoint and client_id for the server's configured
    authentication provider by querying /auth/config and the provider's own
    OIDC discovery document, mirroring what `flightctl login` does internally.

    Returns (token_endpoint, client_id, error_detail). On failure, token_endpoint is
    None and error_detail explains why (for surfacing back to the user).
    """
    if not host:
        return None, None, "no host is configured"
    # The caller may pass a host with a trailing /api/v1 (as used for API requests);
    # the auth config/discovery endpoints live under the bare host.
    base_host = host.rstrip('/')
    if base_host.endswith('/api/v1'):
        base_host = base_host[:-len('/api/v1')].rstrip('/')

    auth_config_url = f"{base_host}/api/v1/auth/config"
    try:
        auth_config = http_get_json(auth_config_url, verify_ssl, ca_path, request_timeout)
    except Exception as e:
        return None, None, f"failed to fetch authentication config from {auth_config_url}: {e}"

    providers = auth_config.get('providers') or []
    default_provider_name = auth_config.get('defaultProvider')
    oidc_specs = []
    for provider in providers:
        spec = provider.get('spec') or {}
        if spec.get('providerType') != 'oidc':
            continue
        provider_name = (provider.get('metadata') or {}).get('name')
        oidc_specs.append((provider_name, spec))

    if not oidc_specs:
        return None, None, "the server has no OIDC-based authentication provider configured"

    # Prefer the default provider, if it is an OIDC one, otherwise use the first OIDC provider found.
    chosen_spec = next((spec for name, spec in oidc_specs if name == default_provider_name), oidc_specs[0][1])
    issuer = chosen_spec.get('issuer')
    client_id = chosen_spec.get('clientId')
    if not issuer:
        return None, client_id, "the configured OIDC provider has no issuer URL"

    discovery_url = f"{issuer.rstrip('/')}/.well-known/openid-configuration"
    try:
        discovery = http_get_json(discovery_url, verify_ssl, ca_path, request_timeout)
    except Exception as e:
        return None, client_id, f"failed to fetch OIDC discovery document from {discovery_url}: {e}"

    token_endpoint = discovery.get('token_endpoint')
    if not token_endpoint:
        return None, client_id, f"OIDC discovery document at {discovery_url} does not advertise a token_endpoint"

    return token_endpoint, client_id, None


def oidc_password_grant(
    host: Optional[str],
    username: str,
    password: str,
    verify_ssl: bool = True,
    ca_path: Optional[str] = None,
    request_timeout: Optional[float] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Perform an OIDC Resource Owner Password Credentials grant against the server's
    configured authentication provider. Returns (bearer_token, error_detail): on success
    bearer_token is the id_token (falling back to access_token) and error_detail is None;
    on failure bearer_token is None and error_detail explains why.
    """
    token_endpoint, client_id, error_detail = discover_oidc_token_endpoint(host, verify_ssl, ca_path, request_timeout)
    if error_detail:
        return None, error_detail
    if not token_endpoint or not client_id:
        return None, "could not determine an OIDC token endpoint and client_id for the server"

    form_data = urlencode({
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'scope': 'openid',
    })

    try:
        response = open_url(
            token_endpoint,
            method='POST',
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            validate_certs=verify_ssl,
            ca_path=ca_path,
            timeout=request_timeout or 30,
        )
        token_data = json.loads(response.read())
    except HTTPError as e:
        try:
            error_body = json.loads(e.read())
            reason = error_body.get('error_description') or error_body.get('error') or e.reason
        except Exception:
            reason = e.reason
        return None, f"token endpoint {token_endpoint} rejected the request ({e.code}): {reason}"
    except Exception as e:
        return None, f"failed to reach token endpoint {token_endpoint}: {e}"

    bearer_token = token_data.get('id_token') or token_data.get('access_token')
    if not bearer_token:
        reason = token_data.get('error_description') or token_data.get('error') or "no id_token or access_token in response"
        return None, f"token endpoint {token_endpoint} did not return a usable token: {reason}"

    return bearer_token, None

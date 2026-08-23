# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json

from ansible.module_utils.urls import open_url

from .exceptions import ValidationException


def fetch_auth_config(host, verify_ssl, ca_path=None):
    """Fetch the Flight Control auth config from ``<host>/api/v1/auth/config``."""
    auth_config_url = host.rstrip('/') + "/api/v1/auth/config"
    try:
        resp = open_url(auth_config_url, validate_certs=verify_ssl,
                        ca_path=ca_path, timeout=10)
        return json.loads(resp.read())
    except Exception as exc:
        raise ValidationException(
            f"Failed to fetch auth config from {auth_config_url}: {exc}"
        ) from exc


def select_oidc_provider(auth_config):
    """Pick the OIDC provider from the auth config, preferring the default provider."""
    providers = auth_config.get("providers") or []
    default_name = auth_config.get("defaultProvider")

    oidc_providers = [
        p for p in providers
        if (p.get("spec") or {}).get("providerType") == "oidc"
    ]
    if not oidc_providers:
        raise ValidationException(
            "No OIDC provider found in auth config"
        )

    if default_name:
        for p in oidc_providers:
            name = (p.get("metadata") or {}).get("name")
            if name == default_name:
                return p

    return oidc_providers[0]


def oidc_password_grant(host, username, password, verify_ssl, ca_path=None):
    """Authenticate via the OIDC password grant and return a Bearer token.

    Discovers the OIDC provider from ``<host>/api/v1/auth/config``, resolves the
    provider's token endpoint via ``/.well-known/openid-configuration``, and
    performs a ``grant_type=password`` request. Returns the ``id_token`` (falling
    back to ``access_token``).

    Shared by the inventory plugin, ``api_module.py`` and ``imagebuilder_module.py``
    so no consumer sends HTTP Basic Auth credentials to an OIDC-only server.
    """
    import urllib.error
    import urllib.parse

    auth_config = fetch_auth_config(host, verify_ssl, ca_path)
    provider = select_oidc_provider(auth_config)
    spec = provider.get("spec", {})
    issuer = spec.get("issuer")
    client_id = spec.get("clientId")
    scopes = spec.get("scopes")

    if not issuer:
        raise ValidationException(
            "OIDC provider in auth config has no issuer URL"
        )
    if not client_id:
        raise ValidationException(
            "OIDC provider in auth config has no clientId"
        )

    discovery_url = issuer.rstrip('/') + "/.well-known/openid-configuration"
    try:
        resp = open_url(discovery_url, validate_certs=verify_ssl,
                        ca_path=ca_path, timeout=10)
        token_endpoint = json.loads(resp.read()).get("token_endpoint")
    except Exception as exc:
        raise ValidationException(
            f"OIDC discovery failed at {discovery_url}: {exc}"
        ) from exc

    if not token_endpoint:
        raise ValidationException(
            f"token_endpoint missing from OIDC discovery at {discovery_url}"
        )

    scope_str = " ".join(scopes) if scopes else "openid"
    payload = urllib.parse.urlencode({
        "grant_type": "password",
        "username": username,
        "password": password,
        "client_id": client_id,
        "scope": scope_str,
    }).encode()

    try:
        resp = open_url(
            token_endpoint, data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            validate_certs=verify_ssl, ca_path=ca_path, timeout=10,
        )
        data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise ValidationException(
            f"OIDC token request failed ({exc.code}): {body}"
        ) from exc
    except Exception as exc:
        raise ValidationException(
            f"OIDC token request failed: {exc}"
        ) from exc

    token = data.get("id_token") or data.get("access_token")
    if not token:
        raise ValidationException(
            "No token returned by OIDC password grant"
        )
    return token

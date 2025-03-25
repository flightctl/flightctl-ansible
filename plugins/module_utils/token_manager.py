import json
import subprocess
import requests
import time
from ansible.parsing.vault import VaultLib

class OIDCTokenManager:
    def __init__(self, oidc_url, client_id, client_secret, username, password, vault_password_file):
        
        self.oidc_url = oidc_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.vault_password_file = vault_password_file
        self.vault = VaultLib(self._load_vault_password())
        self.vault_file = "tokens.vault"
        self.token_endpoint = self._get_token_endpoint()
        self.tokens = self.load_token()
        self._validate_token()

    def _load_vault_password(self):
        with open(self.vault_password_file, "r") as f:
            return f.read().strip().encode()

    def _get_token_endpoint(self):
        response = requests.get(f"{self.oidc_url}/.well-known/openid-configuration")
        response.raise_for_status()
        return response.json().get("token_endpoint")

    def fetch_token(self):
        """Perform password grant login and fetch new tokens."""
        well_known_url = f"{self.oidc_url}/.well-known/openid-configuration"
        config = requests.get(well_known_url).json()
        token_endpoint = config["token_endpoint"]

        response = requests.post(token_endpoint, data={
            "grant_type": "password",
            "client_id": self.client_id,
            "username": self.username,
            "password": self.password,
        })

        response.raise_for_status()

        # Store token data with expiration timestamps
        self.token_data = {
            "access_token": {
                "token": token_data["access_token"],
                "expiry": time.time() + token_data["expires_in"]
            },
            "refresh_token": {
                "token": token_data["refresh_token"],
                "expiry": time.time() + token_data["refresh_expires_in"]
            }
        }

        self._store_token(self.token_data)

    def refresh_token(self, refresh_token):
        """Refresh the access token using the refresh token."""
        well_known_url = f"{self.oidc_url}/.well-known/openid-configuration"
        config = requests.get(well_known_url).json()
        token_endpoint = config["token_endpoint"]

        response = requests.post(token_endpoint, data={
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.token_data["refresh_token"]["token"]
        })
        
        response.raise_for_status()
        token_data = response.json()

        # Update access token and store new expiry
        self.token_data["access_token"] = {
            "token": token_data["access_token"],
            "expiry": time.time() + token_data["expires_in"]
        }
        self._store_token(self.token_data)

    def _store_token(self, tokens):
        encrypted_data = self.vault.encrypt(json.dumps(tokens))
        with open(self.vault_file, "wb") as f:
            f.write(encrypted_data)
        self.tokens = tokens

    def load_token(self):
        try:
            with open(self.vault_file, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = self.vault.decrypt(encrypted_data).decode()
            return json.loads(decrypted_data)
        except (FileNotFoundError, ValueError):
            return {}
        
    def is_token_expired(self, token_type: str) -> bool:
        """Check if the given token is expired."""
        if token_type not in self.token_data:
            return True
        return time.time() >= self.token_data[token_type]["expiry"]

    def _validate_token(self):
        """Ensure a valid access token is available."""
        if "access_token" in self.token_data and not self.is_token_expired("access_token"):
            return 

        if "refresh_token" in self.token_data and not self.is_token_expired("refresh_token"):
            self.refresh_access_token()
        else:
            self.fetch_token()

    def get_access_token(self) -> str:
        """Retrieve a valid access token, refreshing or re-authenticating if necessary."""
        self._validate_token()
        return self.token_data["access_token"]["token"]


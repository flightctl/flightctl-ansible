# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

try:
    import jsonschema
except ImportError as imp_exc:
    JSONSCHEMA_IMPORT_ERROR = imp_exc
else:
    JSONSCHEMA_IMPORT_ERROR = None

try:
    import yaml
except ImportError as imp_exc:
    PYYAML_IMPORT_ERROR = imp_exc
else:
    PYYAML_IMPORT_ERROR = None

from ansible.module_utils.parsing.convert_bool import boolean as strtobool


class ConfigLoader:
    def __init__(self, config_file=None, warn_callback=None):
        if JSONSCHEMA_IMPORT_ERROR:
            raise JSONSCHEMA_IMPORT_ERROR
        if PYYAML_IMPORT_ERROR:
            raise PYYAML_IMPORT_ERROR

        self._warn_callback = warn_callback

        # Assign token from config if it exists
        # Load from config file if provided
        config_data = None
        if config_file:
            config_data = self._load_config_file(config_file)

        # Proceed to assign values from config data if available
        if config_data:
            self._parse_config_data(config_data)

    def _load_config_file(self, config_file):
        """Loads and validates the configuration from the provided file."""
        # Define the schema for validation
        schema = {
            "type": "object",
            "properties": {
                "organization": {"type": "string"},
                "authentication": {
                    "type": "object",
                    "properties": {
                        "access-token": {"type": "string"},
                        "refresh-token": {"type": "string"},
                        "token-to-use": {"type": "string"},
                    },
                },
                "service": {
                    "type": "object",
                    "properties": {
                        "certificate-authority-data": {"type": "string"},  # certificate authority data is a b64 encoded string of a PEM encoded .crt file
                        "server": {"type": "string"},  # server must be a string
                        "insecureSkipVerify": {
                            "type": ["boolean", "string"]
                        },  # insecureSkipVerify can be bool or string
                    },
                    "required": ["server"],  # server field is required
                },
            },
            "required": [
                "authentication",
                "service",
            ],  # authentication and service fields are required
        }

        try:
            # Load the YAML file
            with open(config_file, "r") as file:
                config_data = yaml.load(file, Loader=yaml.SafeLoader)

            # Validate the config file against the schema
            jsonschema.validate(instance=config_data, schema=schema)

        except FileNotFoundError as e:
            raise Exception(f"The file '{config_file}' was not found: {e}") from e
        except yaml.YAMLError as e:
            raise Exception(
                f"Failed to parse YAML file due to a syntax issue: {e}"
            ) from e
        except jsonschema.ValidationError as e:
            raise Exception(f"Schema validation error: {e}") from e
        except Exception as e:
            raise Exception(
                f"An unknown exception occurred while loading config file: {e}"
            ) from e

        return config_data

    def _parse_config_data(self, config_data):
        """Parses and assigns values from config_data."""

        # Assign token from config if it exists
        auth = config_data.get("authentication") or {}

        token_to_use = auth.get("token-to-use")
        access_token = auth.get("access-token")
        refresh_token = auth.get("refresh-token")

        if token_to_use == "refresh":
            if refresh_token:
                setattr(self, "token", refresh_token)
            elif access_token:
                setattr(self, "token", access_token)
            else:
                self._warn(
                    "Config file: token-to-use is 'refresh' but neither refresh-token nor access-token is set."
                )
        elif token_to_use == "access":
            if access_token:
                setattr(self, "token", access_token)
            elif refresh_token:
                setattr(self, "token", refresh_token)
            else:
                self._warn(
                    "Config file: token-to-use is 'access' but neither access-token nor refresh-token is set."
                )
        elif access_token:
            setattr(self, "token", access_token)

        # Assign organization if present in any supported location
        organization = (
            config_data.get("organization")
        )
        if organization:
            setattr(self, "organization", organization)

        # Assign verify_ssl with proper type conversion
        if config_data["service"].get("insecureSkipVerify") is not None:
            verify_ssl_value = config_data["service"]["insecureSkipVerify"]
            if isinstance(verify_ssl_value, str):
                setattr(self, "verify_ssl", not bool(strtobool(verify_ssl_value)))
            else:
                setattr(self, "verify_ssl", not bool(verify_ssl_value))

        # Assign host, username, password, etc., from the config if they exist
        if config_data["service"].get("server"):
            setattr(self, "host", config_data["service"]["server"])

        if config_data["service"].get("certificate-authority-data"):
            setattr(self, "ca_data", config_data["service"]["certificate-authority-data"])

    def _warn(self, message):
        if callable(self._warn_callback):
            self._warn_callback(message)

    def __repr__(self):
        """Represent the current configuration state."""
        return str(self.__dict__)

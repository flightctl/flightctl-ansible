# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


try:
    import jsonschema
except ImportError:
    pass  # Handled by FlightctlModule

try:
    import yaml
except ImportError:
    pass  # Handled by FlightctlModule

from ansible.module_utils.parsing.convert_bool import boolean as strtobool

from .exceptions import FlightctlException


class ConfigLoader:
    def __init__(self, config_file=None):
        config_data = None
        # Assign token from config if it exists
        # Load from config file if provided
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
                "authentication": {
                    "type": "object",
                    "properties": {
                        "token": {"type": "string"}  # token must be a string
                    },
                },
                "service": {
                    "type": "object",
                    "properties": {
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
            raise FlightctlException(
                f"The file '{config_file}' was not found: {e}"
            ) from e
        except yaml.YAMLError as e:
            raise FlightctlException(
                f"Failed to parse YAML file due to a syntax issue: {e}"
            ) from e
        except jsonschema.ValidationError as e:
            raise FlightctlException(f"Schema validation error: {e}") from e
        except Exception as e:
            raise FlightctlException(
                f"An unknown exception occurred while loading config file: {e}"
            ) from e

        return config_data

    def _parse_config_data(self, config_data):
        """Parses and assigns values from config_data."""

        # Assign token from config if it exists
        if config_data["authentication"].get("token"):
            setattr(self, "token", config_data["authentication"]["token"])

        # Assign verify_ssl with proper type conversion
        if config_data["service"].get("insecureSkipVerify") is not None:
            verify_ssl_value = config_data["service"]["insecureSkipVerify"]
            if isinstance(verify_ssl_value, str):
                setattr(self, "verify_ssl", bool(strtobool(verify_ssl_value)))
            else:
                setattr(self, "verify_ssl", bool(verify_ssl_value))

        # Assign host, username, password, etc., from the config if they exist
        if config_data["service"].get("server"):
            setattr(self, "host", config_data["service"]["server"])

    def __repr__(self):
        """Represent the current configuration state."""
        return str(self.__dict__)

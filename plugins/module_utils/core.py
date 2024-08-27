#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


import re
from typing import Any, Optional

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.six.moves.urllib.parse import urlparse

from .config_loader import ConfigLoader
from .exceptions import FlightctlException


class FlightctlModule(AnsibleModule):
    AUTH_ARGSPEC = dict(
        flightctl_host=dict(
            required=False, fallback=(env_fallback, ["FLIGHTCTL_HOST"])
        ),
        flightctl_username=dict(
            required=False, fallback=(env_fallback, ["FLIGHTCTL_USERNAME"])
        ),
        flightctl_password=dict(
            no_log=True, required=False, fallback=(env_fallback, ["FLIGHTCTL_PASSWORD"])
        ),
        flightctl_validate_certs=dict(
            type="bool",
            aliases=["verify_ssl"],
            default=False,
            fallback=(env_fallback, ["FLIGHTCTL_VERIFY_SSL"]),
        ),
        flightctl_request_timeout=dict(
            type="float",
            required=False,
            fallback=(env_fallback, ["FLIGHTCTL_REQUEST_TIMEOUT"]),
        ),
        flightctl_token=dict(
            type="str",
            no_log=True,
            required=False,
            fallback=(env_fallback, ["FLIGHTCTL_TOKEN"]),
        ),
        flightctl_config_file=dict(
            required=False, type="path", aliases=["config_file"]
        ),
    )
    short_params = {
        "host": "flightctl_host",
        "username": "flightctl_username",
        "password": "flightctl_password",
        "verify_ssl": "flightctl_validate_certs",
        "request_timeout": "flightctl_request_timeout",
        "token": "flightctl_token",
    }
    # Default attribute values
    host = None
    url = None
    username = None
    password = None
    verify_ssl = True
    request_timeout = 10
    token = None
    # authenticated = False

    def __init__(
        self,
        argument_spec: Optional[Any] = None,
        error_callback: Optional[Any] = None,
        warn_callback: Optional[Any] = None,
        **kwargs: Any,
    ):
        full_argspec = {}
        full_argspec.update(FlightctlModule.AUTH_ARGSPEC)
        full_argspec.update(argument_spec)
        kwargs["supports_check_mode"] = True

        self.error_callback = error_callback
        self.warn_callback = warn_callback
        self.result = {"changed": False}

        super().__init__(argument_spec=full_argspec, **kwargs)

        # Load configuration files
        self.load_config_files()

        # Parameters specified on command line will override settings in any config
        for short_param, long_param in self.short_params.items():
            direct_value = self.params.get(long_param)
            if direct_value is not None:
                setattr(self, short_param, direct_value)

        # Ensure the host URL is valid
        self.ensure_host_url()

    def ensure_host_url(self) -> None:
        """Ensure the host URL is valid and resolves properly."""
        # Perform some basic validation
        if not re.match("^https{0,1}://", self.host):
            self.host = "https://{0}".format(self.host)

        # Try to parse the hostname as a URL
        try:
            self.url = urlparse(self.host)
            self.url_prefix = self.url.path
        except Exception as e:
            raise FlightctlException(
                f"Unable to parse flightctl_host as a URL ({e}): {self.host}"
            ) from e

    def load_config_files(self) -> None:
        """Load configuration files using ConfigLoader."""
        config_file = self.params.get("flightctl_config_file", None)

        try:
            # Use ConfigLoader to load config from file or fallback to defaults
            config_loader = ConfigLoader(config_file=config_file)

            # Map the loaded config to this module's attributes
            self.map_loaded_config(config_loader)

        except Exception as e:
            raise FlightctlException(f"Failed to load the config file: {e}") from e

    def map_loaded_config(self, config_loader) -> None:
        """Map values from the ConfigLoader to this module's attributes."""
        for module_attr, config_attr in self.short_params.items():
            # Check if the ConfigLoader has the attribute and update module attribute if present
            if hasattr(config_loader, module_attr):
                setattr(self, module_attr, getattr(config_loader, module_attr))

    def logout(self):
        # This method is intended to be overridden
        pass

    def fail_json(self, **kwargs):
        # Try to log out if we are authenticated
        # self.logout()
        if self.error_callback:
            self.error_callback(**kwargs)
        else:
            super().fail_json(**kwargs)

    def exit_json(self, **kwargs):
        # Try to log out if we are authenticated
        # self.logout()
        super().exit_json(**kwargs)

    def warn(self, warning):
        if self.warn_callback is not None:
            self.warn_callback(warning)
        else:
            super().warn(warning)

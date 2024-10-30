# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
from typing import Any, Callable, Dict, Optional

from ansible.module_utils.basic import AnsibleModule, env_fallback, missing_required_lib
from ansible.module_utils.common.text.converters import to_text
from ansible.module_utils.compat.version import LooseVersion
from ansible.module_utils.six.moves.urllib.parse import urlparse

from .config_loader import ConfigLoader
from .exceptions import FlightctlException


class FlightctlModule(AnsibleModule):
    AUTH_ARGSPEC: Dict[str, Any] = dict(
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
            default=True,
            fallback=(env_fallback, ["FLIGHTCTL_VERIFY_SSL"]),
        ),
        flightctl_request_timeout=dict(
            type="float",
            required=False,
            fallback=(env_fallback, ["FLIGHTCTL_REQUEST_TIMEOUT"]),
            aliases=["request_timeout"],
        ),
        flightctl_token=dict(
            type="str",
            no_log=True,
            required=False,
            fallback=(env_fallback, ["FLIGHTCTL_TOKEN"]),
        ),
        flightctl_config_file=dict(
            required=False,
            type="path",
            aliases=["config_file"],
            fallback=(env_fallback, ["FLIGHTCTL_CONFIG_FILE"]),
        ),
    )
    short_params: Dict[str, str] = {
        "host": "flightctl_host",
        "username": "flightctl_username",
        "password": "flightctl_password",
        "verify_ssl": "flightctl_validate_certs",
        "request_timeout": "flightctl_request_timeout",
        "token": "flightctl_token",
    }
    # Default attribute values
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    verify_ssl: bool = True
    request_timeout: float = 10
    token: Optional[str] = None
    # authenticated = False

    default_settings = {
        "check_jsonschema": True,
        "check_pyyaml": True,
        "check_openapi_schema_validator": True,
        "check_jsonpatch": True,
    }

    def __init__(
        self,
        argument_spec: Dict[str, Any],
        error_callback: Optional[Callable[..., None]] = None,
        warn_callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the FlightctlModule.

        Args:
            argument_spec (Optional[Dict[str, Any]]): The arguments for module specification.
            error_callback (Optional[Callable[..., None]]): Callback for handling errors.
            warn_callback (Optional[Callable[[str], None]]): Callback for handling warnings.
            **kwargs (Any): Additional keyword arguments.
        """
        full_argspec: dict[str, Any] = {}
        full_argspec.update(FlightctlModule.AUTH_ARGSPEC)
        full_argspec.update(argument_spec)
        kwargs["supports_check_mode"] = True

        self.error_callback = error_callback
        self.warn_callback = warn_callback
        self.result = {"changed": False}

        local_settings = {}
        for key, value in FlightctlModule.default_settings.items():
            try:
                local_settings[key] = kwargs.pop(key)
            except KeyError:
                local_settings[key] = FlightctlModule.default_settings[key]
        self.settings = local_settings

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

        if self.settings["check_jsonschema"]:
            self.requires("jsonschema")

        if self.settings["check_jsonpatch"]:
            self.requires("jsonpatch")

        if self.settings["check_pyyaml"]:
            self.requires("pyyaml")

        if self.settings["check_openapi_schema_validator"]:
            self.requires("openapi_schema_validator")

    def ensure_host_url(self) -> None:
        """
        Ensure the host URL is valid and resolves properly.
        """
        # Perform some basic validation
        if self.host and not re.match("^https{0,1}://", self.host):
            self.host = f"https://{self.host}"

        # Try to parse the hostname as a URL
        try:
            self.url = urlparse(self.host)
            self.url_prefix = self.url.path
        except Exception as e:
            raise FlightctlException(
                f"Unable to parse flightctl_host as a URL ({e}): {self.host}"
            ) from e

    def load_config_files(self) -> None:
        """
        Load configuration files using ConfigLoader.
        """
        config_file = self.params.get("flightctl_config_file", None)
        if not config_file:
            return

        try:
            # Use ConfigLoader to load config from file or fallback to defaults
            config_loader = ConfigLoader(config_file=config_file)

            # Map the loaded config to this module's attributes
            self.map_loaded_config(config_loader)

        except Exception as e:
            raise FlightctlException(f"Failed to load the config file: {e}") from e

    def map_loaded_config(self, config_loader: ConfigLoader) -> None:
        """
        Map values from the ConfigLoader to this module's attributes.

        Args:
            config_loader (ConfigLoader): The ConfigLoader instance used to load configuration.
        """
        for module_attr, module_value in self.short_params.items():
            # Check if the ConfigLoader has the attribute and update module attribute if present
            if hasattr(config_loader, module_attr):
                setattr(self, module_attr, getattr(config_loader, module_attr))

    def logout(self) -> None:
        # This method is intended to be overridden
        pass

    def fail_json(self, *args, **kwargs: Any) -> None:
        """
        Handle failure by logging out if necessary and then reporting the failure.

        Args:
            **kwargs (Any): Additional arguments for error reporting.
        """
        # Try to log out if we are authenticated
        # self.logout()
        if self.error_callback:
            self.error_callback(**kwargs)
        else:
            super().fail_json(*args, **kwargs)

    def exit_json(self, **kwargs: Any) -> None:
        """
        Handle success by logging out if necessary and then reporting success.

        Args:
            **kwargs (Any): Additional arguments for success reporting.
        """
        # Try to log out if we are authenticated
        # self.logout()
        super().exit_json(**kwargs)

    def warn(self, warning: str) -> None:
        """
        Handle warnings by invoking the warning callback if available.

        Args:
            warning (str): Warning message to be handled.
        """
        if self.warn_callback is not None:
            self.warn_callback(warning)
        else:
            super().warn(warning)

    def requires(
        self,
        dependency: str,
        minimum: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        try:
            requires(dependency, minimum, reason=reason)
        except FlightctlException as e:
            self.fail_json(msg=to_text(e))


def gather_versions() -> dict:
    versions = {}
    try:
        import jsonpatch

        versions["jsonpatch"] = jsonpatch.__version__
    except ImportError:
        pass

    try:
        import jsonschema

        versions["jsonschema"] = jsonschema.__version__
    except ImportError:
        pass

    try:
        import openapi_schema_validator

        versions["openapi_schema_validator"] = openapi_schema_validator.__version__
    except ImportError:
        pass

    try:
        import yaml

        versions["pyyaml"] = yaml.__version__
    except ImportError:
        pass

    return versions


def has_at_least(dependency: str, minimum: Optional[str] = None) -> bool:
    """Check if a specific dependency is present at a minimum version.

    If a minimum version is not specified it will check only that the
    dependency is present.
    """
    dependencies = gather_versions()
    current = dependencies.get(dependency)
    if current is not None:
        if minimum is None:
            return True
        supported = LooseVersion(current) >= LooseVersion(minimum)
        return supported
    return False


def requires(
    dependency: str, minimum: Optional[str] = None, reason: Optional[str] = None
) -> None:
    """Fail if a specific dependency is not present at a minimum version.

    If a minimum version is not specified it will require only that the
    dependency is present. This function raises an exception when the
    dependency is not found at the required version.
    """
    if not has_at_least(dependency, minimum):
        if minimum is not None:
            lib = f"{dependency}>={minimum}"
        else:
            lib = dependency
        raise FlightctlException(missing_required_lib(lib, reason=reason))

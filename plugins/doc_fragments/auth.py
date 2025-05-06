# coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  flightctl_host:
    description:
    - URL to Flight Control server.
    - If value not set, will try environment variable C(FLIGHTCTL_HOST).
    type: str
  flightctl_username:
    description:
    - Username for your Flight Control service.
    - If value not set, will try environment variable C(FLIGHTCTL_USERNAME)
    - Please note that this only works with proxies configured to use HTTP Basic Auth.
    type: str
  flightctl_password:
    description:
    - Password for your Flight Control service.
    - If value not set, will try environment variable C(FLIGHTCTL_PASSWORD)
    - Please read the description of the C(flightctl_username) option for a discussion of
      when this option is applicable.
    type: str
  flightctl_token:
    description:
    - The Flight Control API token to use.
    - This value can be in one of two formats.
    - If value not set, will try environment variable C(FLIGHTCTL_TOKEN)
    type: str
  flightctl_validate_certs:
    description:
    - Whether to allow insecure connections to Flight Control service.
    - If C(false), SSL certificates will not be validated.
    - This should only be used on personally controlled sites using self-signed certificates.
    - If value not set, will try environment variable C(FLIGHTCTL_VERIFY_SSL)
    type: bool
    aliases: [ verify_ssl ]
    default: True
  flightctl_request_timeout:
    description:
    - Specify the timeout Ansible should use in requests to the controller host.
    - Defaults to 10s, but this is handled by the shared module_utils code.
    - If value not set, will try environment variable C(FLIGHTCTL_REQUEST_TIMEOUT).
    type: float
    aliases: [ request_timeout ]
  flightctl_config_file:
    description:
    - Path to the config file.
    - If value not set, will try environment variable C(FLIGHTCTL_CONFIG_FILE).
    type: path
    aliases: [ config_file ]
  flightctl_ca_path:
    description:
    - Path to a CA cert file to use when making requests.
    - If value not set, will try environment variable C(FLIGHTCTL_CA_PATH).
    type: path
    aliases: [ ca_path ]
"""

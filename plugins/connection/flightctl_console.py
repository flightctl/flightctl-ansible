# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
name: flightctl_console
short_description: Connect to Flight Control managed devices
description:
  - This connection plugin allows Ansible to connect to managed Flight Control devices through the API's console endpoint.
author:
  - "Dakota Crowder (@dakcrowder)"
version_added: "0.7.0"
options:
  flightctl_device_name:
    description: The Flight Control device name identifier
    required: True
    type: str
    vars:
      - name: ansible_flightctl_device_name
    env:
      - name: FLIGHTCTL_DEVICE_NAME
  flightctl_config_file:
    description: Path to the config file. If value not set, will try environment variable C(FLIGHTCTL_CONFIG_FILE).
    type: path
    vars:
      - name: ansible_flightctl_config_file
    env:
      - name: FLIGHTCTL_CONFIG_FILE
  flightctl_host:
    description: URL to Flight Control server. If value not set, will try environment variable C(FLIGHTCTL_HOST).
    type: str
    vars:
      - name: ansible_flightctl_host
    env:
      - name: FLIGHTCTL_HOST
  flightctl_token:
    description:
    - The Flight Control API token to use. This value can be in one of two formats.
    - If value not set, will try environment variable C(FLIGHTCTL_TOKEN)
    type: str
    vars:
      - name: ansible_flightctl_token
    env:
      - name: FLIGHTCTL_TOKEN
  flightctl_validate_certs:
    description:
    - Whether to allow insecure connections to Flight Control service. If C(false), SSL certificates will not be validated.
    - This should only be used on personally controlled sites using self-signed certificates.
    - If value not set, will try environment variable C(FLIGHTCTL_VERIFY_SSL)
    type: bool
    vars:
      - name: ansible_flightctl_validate_certs
    env:
      - name: FLIGHTCTL_VERIFY_SSL
  flightctl_ca_path:
    description: Path to a CA cert file to use when making requests. If value not set, will try environment variable C(FLIGHTCTL_CA_PATH).
    type: path
    vars:
      - name: ansible_flightctl_ca_path
    env:
      - name: FLIGHTCTL_CA_PATH
'''


EXAMPLES = r"""
- name: Run a command in a device using passed vars to setup the connection
  hosts: localhost
  gather_facts: false
  vars:
    ansible_connection: flightctl.core.flightctl_console
    ansible_remote_tmp: /var/.ansible/tmp # Default ansible tmp dir is readonly in bootc devices
    ansible_flightctl_device_name: my-device-name
    ansible_flightctl_config_file: ~/.config/flightctl/client.yaml
  tasks:
    # Be aware that the command is executed as root and requires python to be installed on the device
    - name: Run a command in a pod
      ansible.builtin.command: echo "Hello, World!"
      changed_when: false

- name: Run a command in a device using a static inventory file
  # Example inventory:
  # flightctl:
  #   hosts:
  #     example-device-1:
  #       ansible_connection: flightctl.core.flightctl_console
  #       ansible_remote_tmp: /var/.ansible/tmp # Default ansible tmp dir is readonly in bootc devices
  #       ansible_flightctl_device_name: my-device-name
  #       ansible_flightctl_config_file: ~/.config/flightctl/client.yaml
  hosts: flightctl
  gather_facts: false
  tasks:
    # Be aware that the command is executed as root and requires python to be installed on the device
    - name: Run a command in a device
      ansible.builtin.command: echo "Hello, World!"
      changed_when: false
"""


import base64
import json
import os
import re
import ssl
import urllib.parse
from enum import Enum

try:
    from websockets.sync.client import connect
    from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
except ImportError as imp_exc:
    WEBSOCKETS_IMPORT_ERROR = imp_exc
else:
    WEBSOCKETS_IMPORT_ERROR = None

from ansible.plugins.connection import ConnectionBase
from ansible.errors import AnsibleConnectionFailure
from ..module_utils.config_loader import ConfigLoader


CMD_END_MARKER = "__ANSIBLE_CMD_END__"
PUT_FILE_MARKER = "__ANSIBLE_PUT_FILE__"

STD_IN_CHANNEL = 0
STD_OUT_CHANNEL = 1
STD_ERR_CHANNEL = 2
STREAM_ERR_CHANNEL = 3


class CommandType(Enum):
    EXEC = 1
    PUT = 2
    FETCH = 3


class Connection(ConnectionBase):
    """Flight Control connection plugin."""

    # ConnectionBase attributes
    transport = 'flightctl_console'
    has_tty = False

    # Required params
    host_url = None
    device_name = None

    # Optional params
    token = None
    validate_certs = None
    ca_path = None
    ca_data = None

    # Config file representation
    config_file = None

    # Websocket state
    _ws = None

    def __init__(self, *args, **kwargs):
        if WEBSOCKETS_IMPORT_ERROR:
            raise WEBSOCKETS_IMPORT_ERROR

        super(Connection, self).__init__(*args, **kwargs)

    def _get_param(self, option_name, config_attr=None):
        """Get a parameter value from ansible provided config or flighttl config file."""
        # 1. Check get_option
        value = self.get_option(option_name)
        if value is not None:
            return value

        # 2. Check loaded config file
        if config_attr and self.config_file:
            value = getattr(self.config_file, config_attr, None)
            if value is not None:
                return value

        # 3. Return None if not found
        return None

    def _set_device_name(self):
        self.device_name = self._get_param('flightctl_device_name')
        if not self.device_name:
            raise AnsibleConnectionFailure("flightctl_device_name must be specified")

    def _set_host_url(self):
        self.host_url = self._get_param('flightctl_host', 'host')
        if not self.host_url:
            raise AnsibleConnectionFailure("flightctl_host must be specified")

    def _set_token(self):
        self.token = self._get_param('flightctl_token', 'token')

    def _set_validate_certs(self):
        validate_certs_opt = self._get_param('flightctl_validate_certs')
        validate_certs_cfg = getattr(self.config_file, 'verify_ssl', None)

        if validate_certs_opt is not None:
            self.validate_certs = validate_certs_opt
        elif validate_certs_cfg is not None:
            self.validate_certs = validate_certs_cfg
        else:
            self.validate_certs = True

    def _set_ca_cert(self):
        self.ca_path = self._get_param('flightctl_ca_path')

        if self.ca_path:
            return

        # ca_data is only loaded from config file, not env or options
        encoded_ca_data = getattr(self.config_file, 'ca_data', None)
        if encoded_ca_data:
            try:
                self.ca_data = base64.b64decode(encoded_ca_data).decode('utf-8')
            except (base64.binascii.Error, UnicodeDecodeError) as e:
                raise AnsibleConnectionFailure("Invalid CA data – cannot decode base64-encoded PEM") from e

    def _set_connection_params(self):
        """Set connection parameters from passed configuration."""
        # Load config file if provided
        config_file_path = self.get_option('flightctl_config_file')
        if config_file_path and not os.path.exists(config_file_path):
            raise AnsibleConnectionFailure(f"Config file {config_file_path} does not exist")
        if config_file_path:
            self.config_file = ConfigLoader(config_file=config_file_path)

        self._set_device_name()
        self._set_host_url()
        self._set_token()
        self._set_validate_certs()
        # Note: _set_ca_cert is dependent on validate_certs state
        # so it should be called after _set_validate_certs
        self._set_ca_cert() if self.validate_certs else None

        self._display.vvv(
            f"Connection info:\n"
            f"  host={self.host_url}\n"
            f"  device_name={self.device_name}\n"
            f"  has_token={bool(self.token)}\n"
            f"  validate_certs={self.validate_certs}"
        )

    def _build_ssl_context(self):
        """Build SSL context for the WebSocket connection."""
        if self.validate_certs:
            if self.ca_path:
                return ssl.create_default_context(cafile=self.ca_path)
            elif self.ca_data:
                return ssl.create_default_context(cadata=self.ca_data)
            else:
                return ssl.create_default_context()
        else:
            return ssl._create_unverified_context()

    def _connect(self):
        """Open websocket connection using synchronous API."""
        self._display.vvv("Opening WebSocket connection")
        # Set connection parameters
        self._set_connection_params()

        ws_url = self._build_websocket_url()
        self._display.vvv(f"Connecting to WebSocket URL: {ws_url}")

        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"

        try:
            self._ws = connect(
                ws_url,
                additional_headers=headers,
                ssl_context=self._build_ssl_context(),
                subprotocols=["v5.channel.k8s.io"],
            )
            return self
        except Exception as e:
            raise AnsibleConnectionFailure(f"WebSocket connect failed {e}") from e

    def _build_websocket_url(self):
        """Builds a proper WebSocket URL from host URL."""
        # Remove any trailing slashes
        host_url = self.host_url.rstrip('/')

        # Strip the https protocol if present
        if re.match("^https{0,1}://", host_url):
            host_url = host_url.split("://", 1)[1]

        # Add wss:// prefix if not already present
        if not host_url.startswith("wss://"):
            host_url = f"wss://{host_url}"

        metadata = self._build_metadata()
        encoded_metadata = urllib.parse.quote(metadata)

        return f"{host_url}/ws/v1/devices/{self.device_name}/console?metadata={encoded_metadata}"

    def _build_metadata(self):
        """Build the JSON metadata payload for a command."""
        metadata = {
            "tty": False,
            "command": {
                "command": "",
                "args": [],
            },
        }
        return json.dumps(metadata)

    def exec_command(self, cmd, in_data=None, sudoable=False):
        """Run a bash command over the websocket."""
        if in_data:
            raise AnsibleConnectionFailure("Pipelining not supported")

        if not self._ws:
            self._connect()

        try:
            stdout, stderr = self._send_command(cmd, CommandType.EXEC)
            return 0, stdout.encode(), stderr.encode()
        except Exception as e:
            raise AnsibleConnectionFailure("exec_command failed") from e

    def _build_command(self, cmd, type):
        """Build the command string to be sent over the WebSocket."""
        full_cmd = cmd.strip()
        log_cmd = ""
        if type == CommandType.EXEC:
            log_cmd = "echo exec_command | systemd-cat -t ansible-console"
        elif type == CommandType.PUT:
            log_cmd = "echo put_file | systemd-cat -t ansible-console"
        elif type == CommandType.FETCH:
            log_cmd = "echo fetch_file | systemd-cat -t ansible-console"

        if log_cmd:
            full_cmd = f"{log_cmd}\n{full_cmd}"

        return full_cmd + f'\necho {CMD_END_MARKER}\n'

    def _send_command(self, cmd, type):
        """Send a command over the WebSocket and receive output/error streams.

        This method implements communication against the v5.channel.k8s.io subprotocol.

        The subprotocol is a simple framing protocol. Each message is prefixed with a single byte
        indicating the channel number (0, 1, or 2) followed by the message content. The message
        content is a UTF-8 encoded string. The channel numbers are by convention defined to match
        the POSIX file-descriptors assigned to STDIN, STDOUT, and STDERR (0, 1, and 2).

        Commands are sent on channel 0 (STDIN) and the output is received on channel 1 (STDOUT).
        Any error output is received on channel 2 (STDERR). Channel 3 indicates a remote error.

        Sent commands are terminated with a special marker (CMD_END_MARKER) echoed to STDOUT
        to indicate the end of the command output.

        Args:
            cmd: The command string to execute on the remote device.

        Returns:
            A tuple containing the captured stdout and stderr as strings.

        Raises:
            AnsibleConnectionFailure: If the WebSocket is not connected or if a remote stream error occurs.
            Exception: For other unexpected errors during WebSocket communication.
        """
        if not self._ws:
            raise AnsibleConnectionFailure("WebSocket is not connected.")

        try:
            full_cmd = self._build_command(cmd, type)
            self._ws.send(bytes([STD_IN_CHANNEL]) + full_cmd.encode())

            output = ""
            err_output = ""
            while True:
                msg = self._ws.recv()
                channel = msg[0]
                content = msg[1:].decode(errors="ignore")

                if channel == STD_OUT_CHANNEL:
                    output += content

                    # Only break if we received CMD_END_MARKER
                    if CMD_END_MARKER in output:
                        break
                elif channel == STD_ERR_CHANNEL:
                    err_output += content
                elif channel == STREAM_ERR_CHANNEL:
                    raise Exception("Stream error occurred: " + content)

            return output.replace(CMD_END_MARKER, "").strip(), err_output.strip()
        except (ConnectionClosedOK, ConnectionClosedError):
            self._ws = None  # Clear the websocket reference since it's no longer usable
            raise AnsibleConnectionFailure("WebSocket is not connected")
        except Exception as e:
            raise AnsibleConnectionFailure("Error during command execution") from e

    def put_file(self, in_path, out_path):
        """Upload a file by streaming its contents over stdin."""
        try:
            # Read file contents and encode in base64
            with open(in_path, 'rb') as f:
                content = f.read()

            b64content = base64.b64encode(content).decode()

            # Create a command that will decode the base64 data and write to the output file
            cmd = f"mkdir -p $(dirname '{out_path}') && cat << '{PUT_FILE_MARKER}' | base64 -d > '{out_path}'\n{b64content}\n{PUT_FILE_MARKER}"

            self._display.vvv(f"Copying file to {out_path}")

            self._send_command(cmd, CommandType.PUT)
        except Exception as e:
            raise AnsibleConnectionFailure("put_file failed") from e

    def fetch_file(self, in_path, out_path):
        """Download a file from the remote system to the local system."""
        try:
            self._display.vvv(f"Fetching file from {in_path} to {out_path}")

            # Read the remote file and encode it as base64
            cmd = f"cat '{in_path}' 2>/dev/null | base64"
            stdout, stderr = self._send_command(cmd, CommandType.FETCH)

            if stderr:
                raise AnsibleConnectionFailure(f"Error reading remote file: {stderr}")

            if not stdout:
                raise AnsibleConnectionFailure(f"Remote file {in_path} not found or is empty")

            # Decode the base64 content
            try:
                content = base64.b64decode(stdout)
            except Exception as e:
                raise AnsibleConnectionFailure(f"Failed to decode base64 content: {e}") from e

            # Create the local directory if it doesn't exist
            local_dir = os.path.dirname(out_path)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            # Write the content to the local file
            with open(out_path, 'wb') as f:
                f.write(content)
        except Exception as e:
            raise AnsibleConnectionFailure(f"fetch_file failed {e}") from e

    def reset(self):
        """Reset the connection to the device."""
        self._display.vvv("Resetting connection")
        self.close()
        self._connect()

    def close(self):
        """Close websocket if open."""
        if self._ws:
            try:
                self._ws.close()
            except Exception as e:
                self._display.vvv(f"Error closing WebSocket: {e}")
            finally:
                self._ws = None

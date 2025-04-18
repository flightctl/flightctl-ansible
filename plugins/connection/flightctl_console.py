#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: flightctl_console
    short_description: Connect to Flight Control managed devices
    description:
        - This connection plugin allows Ansible to connect to managed FlightControl devices through the FlightControl API's console endpoint.
        - It uses WebSockets to establish a persistent connection, which is maintained for the duration of the Ansible playbook run.
    author:
    - "Dakota Crowder (@dakcrowder)"
    version_added: "0.6.0"
    options:
      flightctl_device_name:
        description: The FlightControl device name identifier
        default: ''
        vars:
          - name: ansible_flightctl_device_name
        env:
          - name: ANSIBLE_FLIGHTCTL_DEVICE_NAME
      flightctl_api_url:
        description: URL for the FlightControl API server
        default: 'localhost:3443'
        vars:
          - name: ansible_flightctl_api_url
        env:
          - name: ANSIBLE_FLIGHTCTL_API_URL
      flightctl_token:
        description: Authentication token for the FlightControl API
        default: ''
        vars:
          - name: ansible_flightctl_token
        env:
          - name: ANSIBLE_FLIGHTCTL_TOKEN
          - name: FLIGHTCTL_TOKEN
      flightctl_use_ssl:
        description: Whether to use SSL/TLS for the connection
        default: true
        type: boolean
        vars:
          - name: ansible_flightctl_use_ssl
        env:
          - name: ANSIBLE_FLIGHTCTL_USE_SSL
'''

import asyncio
import json
import os
import ssl
import urllib.parse
from contextlib import asynccontextmanager

try:
    import websockets
    from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
except ImportError as imp_exc:
    WEBSOCKETS_IMPORT_ERROR = imp_exc
else:
    WEBSOCKETS_IMPORT_ERROR = None

from ansible.plugins.connection import ConnectionBase
from ansible.errors import AnsibleConnectionFailure


CMD_END_MARKER = "__ANSIBLE_CMD_END__"

class Connection(ConnectionBase):
    transport = 'flightctl_console'
    has_persistent_connections = True
    has_tty = False

    def __init__(self, *args, **kwargs):
        if WEBSOCKETS_IMPORT_ERROR:
            raise WEBSOCKETS_IMPORT_ERROR

        super(Connection, self).__init__(*args, **kwargs)
        self._loop = None
        self._ws = None  # Persistent websocket

        # Plugin options
        self.plugin_options = {
            'flightctl_device_name': {},
            'flightctl_api_url': {},
            'flightctl_token': {},
            'flightctl_use_ssl': {'default': True, 'type': 'boolean'},
        }

    def _get_loop(self):
        """Get or create the asyncio event loop."""
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop

    def _run_async(self, coro):
        """Run an async coroutine."""
        loop = self._get_loop()
        try:
            return loop.run_until_complete(coro)
        except RuntimeError as e:
            if "already running" in str(e):
                return asyncio.get_event_loop().run_until_complete(coro)
            raise

    def _get_connection_params(self):
        device = self.get_option('flightctl_device_name')
        if not device:
            raise AnsibleConnectionFailure("flightctl_device_name must be specified")
        api_url = self.get_option('flightctl_api_url')
        token = self.get_option('flightctl_token') or os.getenv('FLIGHTCTL_TOKEN')
        use_ssl = self.get_option('flightctl_use_ssl')
        return device, api_url, token, use_ssl

    @asynccontextmanager
    async def _open_websocket(self):
        """Context manager to open persistent websocket."""
        device, api_url, token, use_ssl = self._get_connection_params()

        metadata = self._build_metadata()
        encoded_metadata = urllib.parse.quote(metadata)
        ws_url = f"wss://{api_url}/ws/v1/devices/{device}/console?metadata={encoded_metadata}"

        headers = {}
        if token:
            headers['Authorization'] = f"Bearer {token}"
        ssl_ctx = ssl._create_unverified_context()
        try:
            ws = await websockets.connect(
                ws_url,
                additional_headers=headers,
                ssl=ssl_ctx,
                subprotocols=["v5.channel.k8s.io"],
            )
            yield ws
        except Exception as e:
            raise AnsibleConnectionFailure(f"WebSocket connect failed: {e}")

    def _connect(self):
        """Open persistent websocket connection"""
        self._display.vvv("Opening persistent WebSocket connection...")
        # Establish and cache websocket
        self._ws = self._run_async(self._open_websocket().__aenter__())
        return self

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
        """Run a bash -c command over the persistent websocket."""
        if in_data:
            raise AnsibleConnectionFailure("Pipelining not supported")

        if not self._ws:
            self._connect()

        self._display.vvv(f"Running command: {cmd}")

        try:
            stdout, stderr = self._run_async(self._send_command(cmd))
            return 0, stdout.encode(), stderr.encode()
        except ConnectionClosedOK as e:
            raise AnsibleConnectionFailure(f"WebSocket connection closed during command execution: {e}")
        except ConnectionClosedError as e:
            raise AnsibleConnectionFailure(f"WebSocket connection error: {e}")
        except Exception as e:
            raise AnsibleConnectionFailure(f"exec_command failed: {e}")

    # We are implementing against the v5.channel.k8s.io subprotocol
    #
    # The subprotocol is a simple framing protocol. Each message is prefixed with a single byte
    # indicating the channel number (0, 1, or 2) followed by the message content. The message
    # content is a UTF-8 encoded string. The channel numbers are by convention defined to match
    # the POSIX file-descriptors assigned to STDIN, STDOUT, and STDERR (0, 1, and 2).
    #
    # Commands are sent on channel 0 (STDIN) and the output is received on channel 1 (STDOUT).
    # Any error output is received on channel 2 (STDERR).
    #
    # Sent commands are terminated with a special marker "__ANSIBLE_CMD_END__" to indicate the end of the command
    # output. The command is also wrapped in a JSON object to provide metadata about the command
    async def _send_command(self, cmd):
        full_cmd = cmd + f'\necho {CMD_END_MARKER}\n'
        await self._ws.send(b'\x00' + full_cmd.encode())

        output = ""
        errOutput = ""
        while True:
            msg = await self._ws.recv()
            channel = msg[0]
            content = msg[1:].decode(errors="ignore")

            self._display.vvv(f"Received message on channel {channel}: {content}")

            if channel == 1:
                output += content
                # Only break if we're looking for CMD_END_MARKER
                if CMD_END_MARKER in content:
                    break
            elif channel == 2:
                errOutput += content
            elif channel == 3:
                raise Exception("Stream error occurred: " + content)

        return output.replace(CMD_END_MARKER, "").strip(), errOutput.strip()

    def put_file(self, in_path, out_path):
        """Upload a file by streaming its contents over stdin."""
        import base64

        try:
            # Read file contents and encode in base64
            with open(in_path, 'rb') as f:
                content = f.read()

            b64content = base64.b64encode(content).decode()

            # Create a command that will decode the base64 data and write to the output file
            cmd = f"mkdir -p $(dirname '{out_path}') && cat << 'EOF_ANSIBLE_PUT_FILE' | base64 -d > '{out_path}'\n{b64content}\nEOF_ANSIBLE_PUT_FILE"

            self._display.vvv(f"Copying file to {out_path}")

            # Use the existing _send_command method to execute the file transfer
            self._run_async(self._send_command(cmd))
        except Exception as e:
            raise AnsibleConnectionFailure(f"put_file failed: {str(e)}")

    def fetch_file(self, in_path, out_path):
        raise AnsibleConnectionFailure("fetch_file not supported")

    def close(self):
        """Close persistent websocket if open"""
        if self._ws:
            self._run_async(self._ws.close())
            self._ws = None

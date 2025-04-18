#!/usr/bin/python
# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    name: flightctl_console
    short_description: Connect to devices via FlightControl API's console endpoint
    description:
        - This connection plugin allows Ansible to connect to managed FlightControl devices through the FlightControl API's console endpoint.
    author: FlightControl (@flightctl)
    version_added: "1.0.0"
    options:
      flightctl_device:
        description: The FlightControl device identifier
        default: ''
        vars:
          - name: ansible_flightctl_device
        env:
          - name: ANSIBLE_FLIGHTCTL_DEVICE
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

# Import websocket exception classes
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

from ansible.plugins.connection import ConnectionBase
from ansible.errors import AnsibleConnectionFailure

    # Per the Kubernetes documentation:
    # // The Websocket RemoteCommand subprotocol "channel.k8s.io" prepends each binary message with a
    # // byte indicating the channel number (zero indexed) the message was sent on. Messages in both
    # // directions should prefix their messages with this channel byte. Used for remote execution,
    # // the channel numbers are by convention defined to match the POSIX file-descriptors assigned
    # // to STDIN, STDOUT, and STDERR (0, 1, and 2). No other conversion is performed on the raw
    # // subprotocol - writes are sent as they are received by the server.
    # //
    # // Example client session:
    # //
    # //	CONNECT http://server.com with subprotocol "channel.k8s.io"
    # //	WRITE []byte{0, 102, 111, 111, 10} # send "foo\n" on channel 0 (STDIN)
    # //	READ  []byte{1, 10}                # receive "\n" on channel 1 (STDOUT)
    # //	CLOSE
class Connection(ConnectionBase):
    transport = 'flightctl_console'
    has_persistent_connections = True

    def __init__(self, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self._loop = None
        self._ws = None  # Persistent websocket

        # Plugin options
        self.plugin_options = {
            'flightctl_device': {},
            'flightctl_api_url': {'default': 'localhost:3443'},
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
        device = self.get_option('flightctl_device')
        if not device:
            raise AnsibleConnectionFailure("flightctl_device must be specified")
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
        if not self._ws:
            self._connect()

        self._display.vvv(f"Running command: {cmd}")
        try:
            stdout, stderr = self._run_async(self._send_command(cmd))
            return 0, stdout.encode(), stderr.encode()
        except ConnectionClosedOK:
            self._display.vvv("WebSocket connection closed")
            return 0, b'', b''
        except ConnectionClosedError as e:
            self._display.vvv(f"WebSocket connection error: {e}")
            raise AnsibleConnectionFailure(f"WebSocket connection error: {e}")
        except Exception as e:
            raise AnsibleConnectionFailure(f"exec_command failed: {e}")

    async def _send_command(self, cmd):
        await self._ws.send(b'\x00' + (cmd + '\necho __END__\n').encode())
        output = ""
        errOutput = ""
        while True:
            msg = await self._ws.recv()
            channel = msg[0]
            content = msg[1:].decode(errors="ignore")

            if channel == 1:
                output += content
                if "__END__" in content:
                    break
            elif channel == 2:
                errOutput += content
            elif channel == 3:
                try:
                    meta = json.loads(content)
                    self._display.vvv(f"Received metadata: {meta}")
                    return content, errOutput
                except json.JSONDecodeError:
                    raise Exception("Stream error occurred: " + content)

        self._display.vvv(f"Command output: {output}")
        self._display.vvv(f"Command error output: {errOutput}")

        return output.replace("__END__", "").strip(), errOutput.strip()

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

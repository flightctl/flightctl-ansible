# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64
import pytest
from unittest.mock import MagicMock

from ansible.errors import AnsibleConnectionFailure

from websockets.exceptions import ConnectionClosedError
from plugins.connection.flightctl_console import Connection, CMD_END_MARKER, PUT_FILE_MARKER


class MockConfigLoader:
    def __init__(self):
        self.host = None
        self.token = None
        self.verify_ssl = None
        self.ca_data = None


@pytest.fixture
def mock_conn():
    """Return a mocked connection object."""
    conn = Connection(MagicMock(), MagicMock(), MagicMock())
    conn._display = MagicMock()
    return conn


def set_options(conn, options):
    """Set options for a connection object."""
    conn._options = options.copy()
    # Create the get_option method that draws from _options
    conn.get_option = conn._options.get


@pytest.mark.parametrize("opt_val, cfg_val, expected", [
    (True, None, True),
    (False, None, False),
    (None, True, True),
    (None, False, False),
])
def test_set_validate_certs(mock_conn, opt_val, cfg_val, expected):
    """Test _set_validate_certs with various inputs."""
    # Setup options
    set_options(mock_conn, {'flightctl_validate_certs': opt_val})

    # Setup config file if needed
    if cfg_val is not None:
        mock_conn.config_file = MockConfigLoader()
        mock_conn.config_file.verify_ssl = cfg_val

    mock_conn._set_validate_certs()

    assert mock_conn.validate_certs == expected


def test_set_connection_params__basic(mock_conn):
    """Test that _set_connection_params sets the expected instance attributes."""
    # Configure options and environment
    set_options(mock_conn, {
        'flightctl_device_name': 'test-device',
        'flightctl_host': 'test-host',
        'flightctl_token': 'test-token',
        'flightctl_validate_certs': None
    })

    mock_conn._set_connection_params()

    assert mock_conn.device_name == 'test-device'
    assert mock_conn.host_url == 'test-host'
    assert mock_conn.token == 'test-token'
    assert mock_conn.validate_certs is True


def test_set_connection_params__no_device(mock_conn, monkeypatch):
    """Test that _set_connection_params raises an error when no device name is provided."""
    set_options(mock_conn, {
        'flightctl_host': 'test-host',
    })

    with pytest.raises(AnsibleConnectionFailure, match="flightctl_device_name must be specified"):
        mock_conn._set_connection_params()


def test_set_connection_params__no_host(mock_conn, monkeypatch):
    """Test that _set_connection_params raises an error when no host is provided."""
    set_options(mock_conn, {
        'flightctl_device_name': 'test-device',
    })

    with pytest.raises(AnsibleConnectionFailure, match="flightctl_host must be specified"):
        mock_conn._set_connection_params()


def test_build_websocket_url__https(mock_conn):
    """Test that _build_websocket_url properly constructs the URL w/ an https url."""
    mock_conn.host_url = "https://api.example.com"
    mock_conn.device_name = "test-device"

    url = mock_conn._build_websocket_url()

    assert url.startswith("wss://api.example.com/ws/v1/devices/test-device/console?metadata=")
    assert "command" in url  # Check that metadata is included


def test_build_websocket_url__wss(mock_conn):
    """Test that _build_websocket_url properly constructs the URL w/ a wss url."""
    mock_conn.host_url = "wss://api.example.com"
    mock_conn.device_name = "test-device"

    url = mock_conn._build_websocket_url()

    assert url.startswith("wss://api.example.com/ws/v1/devices/test-device/console?metadata=")
    assert "command" in url  # Check that metadata is included


def test_build_websocket_url__no_protocol(mock_conn):
    """Test that _build_websocket_url properly constructs the URL w/ a base url."""
    mock_conn.host_url = "api.example.com"
    mock_conn.device_name = "test-device"

    url = mock_conn._build_websocket_url()

    assert url.startswith("wss://api.example.com/ws/v1/devices/test-device/console?metadata=")
    assert "command" in url  # Check that metadata is included


def test_send_command__success(mock_conn):
    """Test the _send_command method."""
    mock_ws = MagicMock()
    mock_conn._ws = mock_ws

    # Configure the mock to return specific messages
    mock_ws.recv.side_effect = [
        b'\x01stdout data',
        b'\x02stderr data',
        b'\x01' + f'more data\n{CMD_END_MARKER}'.encode()
    ]

    stdout, stderr = mock_conn._send_command("test command")

    assert "stdout data" in stdout
    assert "more data" in stdout
    assert stderr == "stderr data"
    assert mock_ws.send.call_count == 1
    assert mock_ws.recv.call_count == 3


def test_send_command__stream_error(mock_conn):
    """Test that _send_command raises an exception with the proper message when a stream error occurs."""
    mock_ws = MagicMock()
    mock_conn._ws = mock_ws

    # Configure the mock to return a stream error
    mock_ws.recv.side_effect = [
        b'\x01stdout data',
        b'\x03stream error message',
    ]

    with pytest.raises(AnsibleConnectionFailure) as exc_info:
        mock_conn._send_command("test command")

    # The __cause__ of the connection failure should be an Exception with
    # the stream error message
    inner_exc = exc_info.value.__cause__
    assert isinstance(inner_exc, Exception)
    assert "Stream error occurred: stream error message" in str(inner_exc)


def test_send_command__websocket_closed(mock_conn):
    """Test that _send_command raises an exception when websocket is closed."""
    mock_ws = MagicMock()
    mock_conn._ws = mock_ws

    mock_ws.send.side_effect = ConnectionClosedError(None, None)

    with pytest.raises(AnsibleConnectionFailure, match="WebSocket is not connected"):
        mock_conn._send_command("test command")


def test_send_command__no_websocket(mock_conn):
    """Test that _send_command raises an exception when no websocket is available."""
    # Ensure there's no websocket
    mock_conn._ws = None

    with pytest.raises(AnsibleConnectionFailure, match="WebSocket is not connected"):
        mock_conn._send_command("test command")


def test_exec_command__success(mock_conn):
    """Test that exec_command connects if needed and runs the command."""
    mock_conn._ws = None  # Start with no connection
    mock_conn._connect = MagicMock(return_value=mock_conn)

    mock_send_command = MagicMock(return_value=("stdout: test command", "stderr: test command"))
    mock_conn._send_command = mock_send_command

    rc, stdout, stderr = mock_conn.exec_command("test command")

    assert mock_conn._connect.called
    assert mock_send_command.called
    assert rc == 0
    assert stdout == b"stdout: test command"
    assert stderr == b"stderr: test command"


def test_exec_command__failure(mock_conn):
    """Test that exec_command handles errors properly."""
    mock_conn._ws = MagicMock()

    # Make _send_command raise an exception
    mock_conn._send_command = MagicMock(side_effect=Exception("Command execution failed"))

    with pytest.raises(AnsibleConnectionFailure, match="exec_command failed"):
        mock_conn.exec_command("failing command")


def test_put_file__success(mock_conn, tmp_path):
    """Test that put_file reads the file and sends the appropriate command."""
    test_file_content = "test content"
    test_file = tmp_path / "testfile"
    test_file.write_text(test_file_content)
    remote_path = "/remote/path/file"

    # Mock _send_command to return a simple success result
    send_command_mock = MagicMock(return_value=("", ""))
    mock_conn._send_command = send_command_mock

    mock_conn.put_file(str(test_file), remote_path)

    expected_b64_content = base64.b64encode(test_file_content.encode()).decode()
    expected_cmd = (
        f"mkdir -p $(dirname '{remote_path}') && cat << '{PUT_FILE_MARKER}' | base64 -d > '{remote_path}'\n"
        f"{expected_b64_content}\n"
        f"{PUT_FILE_MARKER}"
    )

    # Check _send_command was called with the right arguments
    send_command_mock.assert_called_once_with(expected_cmd)


def test_put_file__failure(mock_conn, tmp_path):
    """Test that put_file handles failures properly."""
    mock_conn._ws = MagicMock()

    # Create a test file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")

    # Make _send_command raise an exception when putting file
    mock_conn._send_command = MagicMock(side_effect=Exception("File transfer failed"))

    with pytest.raises(AnsibleConnectionFailure, match="put_file failed"):
        mock_conn.put_file(str(test_file), "/remote/path")


def test_fetch_file__success(mock_conn, tmp_path):
    """Test that fetch_file gets the file and saves it properly."""
    test_content = "test remote content"
    encoded_content = base64.b64encode(test_content.encode()).decode()
    send_command_mock = MagicMock(return_value=(encoded_content, ""))
    mock_conn._send_command = send_command_mock

    # Setup output file path using pytest's tmp_path fixture
    out_dir = tmp_path / "output_dir"
    out_file = out_dir / "fetched_file.txt"

    mock_conn.fetch_file("/remote/path", str(out_file))

    send_command_mock.assert_called_once_with("cat '/remote/path' 2>/dev/null | base64")

    assert out_dir.exists()
    assert out_file.exists()
    assert out_file.read_text() == test_content


def test_fetch_file__failure(mock_conn):
    """Test that fetch_file handles failures properly."""
    mock_conn._ws = MagicMock()

    # Make _send_command raise an exception
    mock_conn._send_command = MagicMock(side_effect=Exception("File fetch failed"))

    with pytest.raises(AnsibleConnectionFailure, match="fetch_file failed"):
        mock_conn.fetch_file("/remote/path", "/local/path")


def test_fetch_file__not_found(mock_conn):
    """Test fetch_file when remote file doesn't exist (empty output)."""
    mock_conn._ws = MagicMock()

    # Mock send_command to return empty content (file not found)
    mock_conn._send_command = MagicMock(return_value=("", ""))

    with pytest.raises(AnsibleConnectionFailure) as exc_info:
        mock_conn.fetch_file("/nonexistent/file", "/local/path")

    # Check that the cause was the decode error
    assert "Remote file /nonexistent/file not found or is empty" in str(exc_info.value.__cause__)


def test_fetch_file__decode_error(mock_conn, monkeypatch):
    """Test fetch_file when base64 decode fails."""
    mock_conn._ws = MagicMock()

    mock_conn._send_command = MagicMock(return_value=("some-content", ""))

    # Mock base64.b64decode to raise an error
    def mock_b64decode(data):
        raise base64.binascii.Error("Invalid base64-encoded string")
    monkeypatch.setattr(base64, 'b64decode', mock_b64decode)

    with pytest.raises(AnsibleConnectionFailure) as exc_info:
        mock_conn.fetch_file("/remote/file", "/local/path")

    # Check that the cause was the decode error
    assert "Invalid base64-encoded string" in str(exc_info.value.__cause__)


def test_reset(mock_conn):
    """Test that reset method calls close and then connect."""
    mock_conn._ws = MagicMock()
    mock_conn.close = MagicMock()
    mock_conn._connect = MagicMock(return_value=mock_conn)

    mock_conn.reset()

    mock_conn.close.assert_called_once()
    mock_conn._connect.assert_called_once()


def test_close(mock_conn):
    """Test that close method properly closes the websocket."""
    mock_ws = MagicMock()
    mock_conn._ws = mock_ws

    mock_conn.close()

    assert mock_ws.close.called
    assert mock_conn._ws is None

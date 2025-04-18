# coding: utf-8 -*-

# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import asyncio
import base64
import pytest
from unittest.mock import MagicMock, AsyncMock

from ansible.errors import AnsibleConnectionFailure

from plugins.connection.flightctl_console import Connection, CMD_END_MARKER


class MockConfigLoader:
    def __init__(self):
        self.host = None
        self.token = None
        self.verify_ssl = None
        self.ca_data = None


ConnectionClosedOK = type('ConnectionClosedOK', (Exception,), {})
ConnectionClosedError = type('ConnectionClosedError', (Exception,), {})


@pytest.fixture(autouse=True)
def setup_module_patches(monkeypatch):
    """Setup mocks for the tests."""
    # Mock ConfigLoader
    monkeypatch.setattr('plugins.module_utils.config_loader.ConfigLoader', MockConfigLoader)

    # Mock websockets with proper exception classes
    mock_websockets = MagicMock()
    mock_websockets.ConnectionClosedOK = ConnectionClosedOK
    mock_websockets.ConnectionClosedError = ConnectionClosedError
    monkeypatch.setattr('websockets.connect', AsyncMock())

    # Make the mocked module available for tests
    monkeypatch.setattr('plugins.connection.flightctl_console.websockets', mock_websockets)
    monkeypatch.setattr('plugins.connection.flightctl_console.ConnectionClosedOK', ConnectionClosedOK)
    monkeypatch.setattr('plugins.connection.flightctl_console.ConnectionClosedError', ConnectionClosedError)

    yield


@pytest.fixture
def mock_conn():
    """Return a mocked connection object."""
    conn = Connection(MagicMock(), MagicMock(), MagicMock())
    conn._display = MagicMock()

    # Create and use a mock event loop
    mock_loop = asyncio.new_event_loop()
    conn._get_loop = MagicMock(return_value=mock_loop)
    conn._run_async = MagicMock()
    conn._run_async.side_effect = mock_loop.run_until_complete

    return conn


def set_options(conn, options):
    """Set options for a connection object."""
    conn._options = options.copy()
    # Create the get_option method that draws from _options
    conn.get_option = conn._options.get


@pytest.mark.parametrize("opt_val, env_val, cfg_val, expected", [
    (True, None, None, True),
    (False, None, None, False),
    (None, 'true', None, True),
    (None, 'false', None, False),
    (None, None, True, True),
    (None, None, False, False),
])
def test_set_validate_certs(mock_conn, monkeypatch, opt_val, env_val, cfg_val, expected):
    """Test _set_validate_certs with various inputs."""
    # Setup options
    set_options(mock_conn, {'flightctl_validate_certs': opt_val})

    # Setup config file if needed
    if cfg_val is not None:
        mock_conn.config_file = MockConfigLoader()
        mock_conn.config_file.verify_ssl = cfg_val

    # Setup environment if needed
    if env_val is not None:
        monkeypatch.setenv('FLIGHTCTL_VERIFY_SSL', env_val)
    else:
        monkeypatch.delenv('FLIGHTCTL_VERIFY_SSL', raising=False)

    # Call the method
    mock_conn._set_validate_certs()

    # Assert the expected value
    assert mock_conn.validate_certs == expected


def test_set_connection_params_basic(mock_conn):
    """Test that _set_connection_params sets the expected instance attributes."""
    # Configure options and environment
    set_options(mock_conn, {
        'flightctl_device_name': 'test-device',
        'flightctl_host': 'test-host',
        'flightctl_token': 'test-token',
        'flightctl_validate_certs': None
    })

    # Execute
    mock_conn._set_connection_params()

    # Verify
    assert mock_conn.device_name == 'test-device'
    assert mock_conn.host_url == 'test-host'
    assert mock_conn.token == 'test-token'
    assert mock_conn.validate_certs is True


def test_set_connection_params_no_device(mock_conn, monkeypatch):
    """Test that _set_connection_params raises an error when no device name is provided."""
    set_options(mock_conn, {
        'flightctl_host': 'test-host',
    })

    with pytest.raises(AnsibleConnectionFailure, match="flightctl_device_name must be specified"):
        mock_conn._set_connection_params()


def test_set_connection_params_no_host(mock_conn, monkeypatch):
    """Test that _set_connection_params raises an error when no host is provided."""
    set_options(mock_conn, {
        'flightctl_device_name': 'test-device',
    })

    with pytest.raises(AnsibleConnectionFailure, match="flightctl_host must be specified"):
        mock_conn._set_connection_params()


def test_build_websocket_url(mock_conn):
    """Test that _build_websocket_url properly constructs the URL."""
    mock_conn.host_url = "https://api.example.com"
    mock_conn.device_name = "test-device"

    url = mock_conn._build_websocket_url()

    assert url.startswith("wss://api.example.com/ws/v1/devices/test-device/console?metadata=")
    assert "command" in url  # Check that metadata is included


@pytest.mark.asyncio
async def test_send_command(mock_conn):
    """Test the _send_command method."""
    mock_ws = AsyncMock()
    mock_conn._ws = mock_ws

    # Configure the mock to return specific messages
    mock_ws.recv.side_effect = [
        b'\x01stdout data',
        b'\x02stderr data',
        b'\x01' + f'more data\n{CMD_END_MARKER}'.encode()
    ]

    stdout, stderr = await mock_conn._send_command("test command")

    assert "stdout data" in stdout
    assert "more data" in stdout
    assert stderr == "stderr data"
    assert mock_ws.send.await_count == 1
    assert mock_ws.recv.await_count == 3


@pytest.mark.asyncio
async def test_send_command_websocket_closed(mock_conn):
    """Test that _send_command raises an exception when websocket is closed."""
    mock_ws = AsyncMock()
    mock_conn._ws = mock_ws

    mock_ws.send.side_effect = ConnectionClosedError()

    with pytest.raises(AnsibleConnectionFailure, match="WebSocket is not connected"):
        await mock_conn._send_command("test command")


@pytest.mark.asyncio
async def test_send_command_no_websocket(mock_conn):
    """Test that _send_command raises an exception when no websocket is available."""
    # Ensure there's no websocket
    mock_conn._ws = None

    with pytest.raises(AnsibleConnectionFailure, match="WebSocket is not connected"):
        await mock_conn._send_command("test command")


def test_exec_command(mock_conn):
    """Test that exec_command connects if needed and runs the command."""
    mock_conn._ws = None  # Start with no connection
    mock_conn._connect = MagicMock(return_value=mock_conn)

    async def mock_send_command(cmd):
        return f"stdout: {cmd}", f"stderr: {cmd}"

    mock_send_command = AsyncMock(side_effect=mock_send_command)
    mock_conn._send_command = mock_send_command

    rc, stdout, stderr = mock_conn.exec_command("test command")

    assert mock_conn._connect.called
    assert mock_send_command.called
    assert rc == 0
    assert stdout == b"stdout: test command"
    assert stderr == b"stderr: test command"


def test_exec_command_failure(mock_conn):
    """Test that exec_command handles errors properly."""
    mock_conn._ws = AsyncMock()

    # Make _send_command raise an exception
    async def failing_send_command(cmd):
        raise Exception("Command execution failed")

    mock_conn._send_command = failing_send_command

    with pytest.raises(AnsibleConnectionFailure, match="exec_command failed: .*"):
        mock_conn.exec_command("failing command")


def test_put_file(mock_conn, tmp_path):
    """Test that put_file reads the file and sends the appropriate command."""
    test_file_content = "test content"
    test_file = tmp_path / "testfile"
    test_file.write_text(test_file_content)
    remote_path = "/remote/path/file"

    # Mock _send_command to return a simple success result
    send_command_mock = AsyncMock(return_value=("", ""))
    mock_conn._send_command = send_command_mock
    mock_conn._run_async = MagicMock()

    mock_conn.put_file(str(test_file), remote_path)

    expected_b64_content = base64.b64encode(test_file_content.encode()).decode()
    expected_cmd = (
        f"mkdir -p $(dirname '{remote_path}') && cat << 'EOF_ANSIBLE_PUT_FILE' | base64 -d > '{remote_path}'\n"
        f"{expected_b64_content}\n"
        "EOF_ANSIBLE_PUT_FILE"
    )

    assert mock_conn._run_async.called

    # We can't easily check the coroutine contents directly, so check
    # that _send_command was called with the right arguments
    send_command_mock.assert_called_once_with(expected_cmd)


def test_put_file_failure(mock_conn, tmp_path):
    """Test that put_file handles failures properly."""
    mock_conn._ws = AsyncMock()

    # Create a test file
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content")

    # Make _run_async raise an exception when putting file
    def failing_run_async(coro):
        raise Exception("File transfer failed")

    mock_conn._run_async = MagicMock(side_effect=failing_run_async)

    with pytest.raises(AnsibleConnectionFailure, match="put_file failed: .*"):
        mock_conn.put_file(str(test_file), "/remote/path")


def test_fetch_file(mock_conn, tmp_path):
    """Test that fetch_file gets the file and saves it properly."""
    test_content = "test remote content"
    encoded_content = base64.b64encode(test_content.encode()).decode()
    send_command_mock = AsyncMock(return_value=(encoded_content, ""))
    mock_conn._send_command = send_command_mock

    # Setup output file path using pytest's tmp_path fixture
    out_dir = tmp_path / "output_dir"
    out_file = out_dir / "fetched_file.txt"

    mock_conn.fetch_file("/remote/path", str(out_file))

    send_command_mock.assert_called_once_with("cat '/remote/path' 2>/dev/null | base64")

    assert out_dir.exists()
    assert out_file.exists()
    assert out_file.read_text() == test_content


def test_fetch_file_failure(mock_conn):
    """Test that fetch_file handles failures properly."""
    mock_conn._ws = AsyncMock()

    # Make _run_async raise an exception
    def failing_run_async(coro):
        raise Exception("File fetch failed")

    mock_conn._run_async = MagicMock(side_effect=failing_run_async)

    with pytest.raises(AnsibleConnectionFailure, match="fetch_file failed: .*"):
        mock_conn.fetch_file("/remote/path", "/local/path")


def test_fetch_file_not_found(mock_conn):
    """Test fetch_file when remote file doesn't exist (empty output)."""
    mock_conn._ws = AsyncMock()

    # Mock send_command to return empty content (file not found)
    async def mock_send_empty(cmd):
        return "", ""
    mock_conn._send_command = mock_send_empty

    with pytest.raises(AnsibleConnectionFailure, match="Remote file .* not found or is empty"):
        mock_conn.fetch_file("/nonexistent/file", "/local/path")


def test_fetch_file_decode_error(mock_conn, monkeypatch):
    """Test fetch_file when base64 decode fails."""
    mock_conn._ws = AsyncMock()

    async def mock_send(cmd):
        return "some-content", ""
    mock_conn._send_command = mock_send

    # Mock base64.b64decode to raise an error
    def mock_b64decode(data):
        raise base64.binascii.Error("Invalid base64-encoded string")
    monkeypatch.setattr(base64, 'b64decode', mock_b64decode)

    with pytest.raises(AnsibleConnectionFailure, match="Failed to decode base64 content"):
        mock_conn.fetch_file("/remote/file", "/local/path")


def test_reset(mock_conn):
    """Test that reset method calls close and then connect."""
    mock_conn._ws = AsyncMock()
    mock_conn.close = MagicMock()
    mock_conn._connect = MagicMock(return_value=mock_conn)

    mock_conn.reset()

    mock_conn.close.assert_called_once()
    mock_conn._connect.assert_called_once()


def test_close(mock_conn):
    """Test that close method properly closes the websocket."""
    mock_ws = AsyncMock()
    mock_conn._ws = mock_ws

    mock_conn.close()

    assert mock_conn._run_async.called

    # Instead of comparing coroutine objects directly, verify that
    # close() was called on the websocket
    mock_ws.close.assert_called_once()
    assert mock_conn._ws is None

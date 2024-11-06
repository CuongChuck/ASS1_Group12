import pytest
from unittest.mock import MagicMock
from tracker import Tracker


@pytest.fixture
def mock_conn():
    # Mock the connection (simulating the socket or other connection object)
    return MagicMock()


def test_send_http_response(mock_conn):
    # Initialize your Tracker
    tracker = Tracker()

    # Setup: Mock the sendall method on the connection to track calls
    mock_conn.sendall = MagicMock()

    # Call the method you want to test (assuming it's called during some interaction)
    # This should internally call send_http_response
    tracker.send_http_response(mock_conn, 200, {"success": True})

    # Assert sendall was called with the correct HTTP response
    expected_response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        "Content-Length: 17\r\n"  # 17 is the length of '{"success": true}'
        "Connection: close\r\n"
        "\r\n"
        '{"success": true}'
    )

    # Check that sendall was called with the expected response
    mock_conn.sendall.assert_called_with(expected_response.encode())


@pytest.fixture
def mock_peer_data():
    """Mock peer data that will be used in the request."""
    return {
        "id": "peer123",
        "ip_address": "192.168.1.1",
        "port": "6881",
        "bitfield": "01010101",  # Example bitfield
    }


def test_handle_get_request(mock_conn, mock_peer_data):
    """Test the handle_get_request method of the Tracker class."""

    # Create the request string using mock data
    request = (
        f"GET /announce?peer_id={mock_peer_data['id']}&peer_ip_address={mock_peer_data['ip_address']}"
        f"&peer_port={mock_peer_data['port']}&bitfield={mock_peer_data['bitfield']} HTTP/1.1\r\n"
        "Host: 127.0.0.1:8888\r\n"
        "User-Agent: CustomClient/1.0\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # Create a mock Tracker instance
    tracker = Tracker()

    # Setup: Mock the send_http_response method to track calls
    tracker.send_http_response = MagicMock()

    # Call the method you want to test
    tracker.handle_get_request(mock_conn, request)

    # Check that send_http_response was called with the correct response
    expected_peer_list = [
        {
            "id": mock_peer_data["id"],
            "ip": mock_peer_data["ip_address"],
            "port": mock_peer_data["port"],
            "bitfield": mock_peer_data["bitfield"],
        }
    ]

    # Verify that send_http_response was called with status 200 and the expected peer list
    tracker.send_http_response.assert_called_with(
        mock_conn, 200, expected_peer_list
    )


def test_handle_get_request_bad_method(mock_conn):
    """Test handling of an invalid HTTP method (not GET)."""
    # Simulate a POST request instead of GET
    request = (
        "POST /announce?peer_id=peer123&peer_ip_address=192.168.1.1&peer_port=6881&bitfield=01010101 HTTP/1.1\r\n"
        "Host: 127.0.0.1:8888\r\n"
        "User-Agent: CustomClient/1.0\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # Create a mock Tracker instance
    tracker = Tracker()

    # Setup: Mock the send_http_response method to track calls
    tracker.send_http_response = MagicMock()

    # Call the method you want to test
    tracker.handle_get_request(mock_conn, request)

    # Verify that a 400 Bad Request response was sent
    tracker.send_http_response.assert_called_with(
        mock_conn, 400, {"error": "Bad Request"}
    )


def test_handle_get_request_missing_peer_id(mock_conn):
    """Test handling when required parameters are missing from the request."""
    # Simulate a GET request missing 'peer_id'
    request = (
        "GET /announce?peer_ip_address=192.168.1.1&peer_port=6881&bitfield=01010101 HTTP/1.1\r\n"
        "Host: 127.0.0.1:8888\r\n"
        "User-Agent: CustomClient/1.0\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    # Create a mock Tracker instance
    tracker = Tracker()

    # Setup: Mock the send_http_response method to track calls
    tracker.send_http_response = MagicMock()

    # Call the method you want to test
    tracker.handle_get_request(mock_conn, request)

    # Verify that a 400 Bad Request response was sent due to missing parameters
    tracker.send_http_response.assert_called_with(
        mock_conn, 400, {"error": "Bad Request, missing parameters"}
    )

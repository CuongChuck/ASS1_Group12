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

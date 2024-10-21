import socket
from collections import defaultdict

# Configuration
CONFIGS = {
    "constants": {"TRACKER_ADDRESS": ("localhost", 8888), "MAX_CONNECTIONS": 8}
}


class Tracker:
    def __init__(self):
        # Dictionary to store which peers own which files
        self.file_owners_list = defaultdict(list)
        # Dictionary to track the sending frequency of peers
        self.send_frequency_list = defaultdict(int)

        # Create and bind the tracker socket using TCP
        tracker_address = CONFIGS["constants"]["TRACKER_ADDRESS"]
        max_connections = CONFIGS["constants"]["MAX_CONNECTIONS"]

        self.tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tracker_socket.bind(tracker_address)
        self.tracker_socket.listen(max_connections)
        print(f"Tracker listening on {tracker_address}")


if __name__ == "__main__":
    tracker = Tracker()

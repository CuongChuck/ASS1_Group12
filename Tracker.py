import socket
import threading
from collections import defaultdict

# Configuration
CONFIGS = {
    "constants": {
        "TRACKER_ADDRESS": ("localhost", 8888),
        "MAX_CONNECTIONS": 8,
        "BUFFER_SIZE": 1024,
    }
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

    def handle_peer(self, connection, address):
        """Handle individual peer requests"""
        print(f"Connection established with peer: {address}")

        try:
            while True:
                data = connection.recv(CONFIGS["constants"]["BUFFER_SIZE"])
                if not data:
                    break  # Client disconnected

                # Process peer request
                print(f"Received from {address}: {data.decode()}")

                # Send response back to peer
                connection.send(b"Tracker received your request")
        except Exception as e:
            print(f"Error handling peer {address}: {e}")
        finally:
            connection.close()

    def run(self):
        """Start the tracker to listen for incoming peer connections"""
        try:
            while True:
                # Accept incoming connections
                connection, address = self.tracker_socket.accept()
                print(f"New connection from {address}")

                # Handle each peer in a separate thread
                threading.Thread(
                    target=self.handle_peer, args=(connection, address)
                ).start()
        except Exception as e:
            print(f"Error running tracker: {e}")
        finally:
            # Ensure socket is closed properly
            self.tracker_socket.close()


if __name__ == "__main__":
    tracker = Tracker()

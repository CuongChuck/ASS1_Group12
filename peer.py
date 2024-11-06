import socket
import threading
import os
import json

from config import CONFIGS


class Peer:
    def __init__(
        self,
        peer_id,
        tracker_host=CONFIGS["TRACKER_HOST"],
        tracker_port=CONFIGS["TRACKER_PORT"],
        base_dir="./peers",
    ):
        self.peer_id = peer_id
        self.tracker_host = tracker_host
        self.tracker_port = tracker_port
        self.base_dir = os.path.join(base_dir, f"peer-{self.peer_id}")
        self.files = {}  # A dict to manage file pieces
        self.connected_peers = []
        self.server_socket = None

        # Ensure the directory exists for this peer
        os.makedirs(self.base_dir, exist_ok=True)

    def send_message(self, conn, content):
        """Send a message to peer or tracker."""
        message = json.dumps(content)
        conn.sendall(message.encode())

    def receive_message(self, conn):
        """Receives a message from the tracker or a peer."""
        try:
            response = conn.recv(CONFIGS["BUFFER_SIZE"]).decode()
            if response:
                response_data = json.loads(response)
                print(f"Received message: {response_data}")
                return response_data
            else:
                print("No message received.")
                return None
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None

    def connect_to_tracker(self):
        """Connects to tracker to register and returns the socket."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.tracker_host, self.tracker_port))
            return s
        except Exception as e:
            print(f"Failed to connect to tracker: {e}")
            return None

    def register_with_tracker(self, conn):
        """Registers this peer with the tracker."""
        try:
            self.send_message(
                conn,
                {
                    "peer_id": self.peer_id,
                    "action": CONFIGS["ACTIONS"]["REGISTER"],
                },
            )
            response = self.receive_message(conn)
            if response:
                print(response)
        except Exception as e:
            print(f"Failed to register with tracker: {e}")

    def run(self):
        conn = self.connect_to_tracker()
        if conn:
            self.register_with_tracker(conn)


if __name__ == "__main__":
    peer_id = 1
    peer = Peer(peer_id)
    peer.run()

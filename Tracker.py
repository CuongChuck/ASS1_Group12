import socket
import threading
from collections import defaultdict
import sys
import json

from config import CONFIGS


class Tracker:
    def __init__(self):
        self.host = CONFIGS["TRACKER_HOST"]
        self.port = CONFIGS["TRACKER_PORT"]
        self.peers = {}

        # Init TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(CONFIGS["MAX_CONNECTIONS"])
        print(f"Tracker is listening on {self.host}:{self.port}")

    def send_message(self, conn, content):
        """Send back a message to peer."""
        message = json.dumps(content)
        conn.sendall(message.encode())

    def receive_message(self, conn):
        """Receives a message from a peer."""
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

    def register_peer(self, peer_id, addr, conn):
        """Registers a peer and sends a success response."""
        if peer_id:
            self.peers[peer_id] = {"addr": addr, "online": True}
            print(f"Registered peer: {peer_id} at {addr}")

            # Send registration success response
            self.send_message(conn, {"success": True})

    def handle_peer(self, conn, addr):
        """Handle individual peer connections."""
        print(f"Connected to peer: {addr}")
        try:
            message = self.receive_message(conn)
            if not message:
                return

            action = message.get("action")

            if action == CONFIGS["ACTIONS"]["REGISTER"]:
                peer_id = message.get("peer_id")
                self.register_peer(peer_id, addr, conn)
            else:
                self.send_message({"error": "Invalid action"})

        except Exception as e:
            print(f"Error handling peer: {e}")
        finally:
            conn.close()

    def run(self):
        """Start the tracker to listen for incoming peer connections."""
        try:
            self.server_socket.settimeout(1)
            while True:
                try:
                    conn, addr = self.server_socket.accept()
                    t = threading.Thread(
                        target=self.handle_peer, args=(conn, addr)
                    )
                    t.daemon = True
                    t.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("Shuting down the tracker...")
            threading.interrupt_all_thread()
        except Exception as e:
            print(f"Error running tracker: {e}")
        finally:
            self.server_socket.close()
            print("Tracker closed.")
            sys.exit(0)


if __name__ == "__main__":
    tracker = Tracker()
    tracker.run()

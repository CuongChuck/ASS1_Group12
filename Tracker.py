import socket
import threading
from collections import defaultdict
import sys

from config import CONFIGS

# Store peer information and file ownership
file_owners = defaultdict(list)


class Tracker:
    def __init__(self):
        self.host = CONFIGS["TRACKER_HOST"]
        self.port = CONFIGS["TRACKER_PORT"]

        # Init TCP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(CONFIGS["MAX_CONNECTIONS"])
        print(f"Tracker is listening on {self.host}:{self.port}")

    def handle_peer(self, conn, addr):
        """Handle individual peer connections."""
        print(f"Connected to peer: {addr}")
        conn.close()

    def run(self):
        """Start the tracker to listen for incoming peer connections."""
        try:
            self.server_socket.settimeout(5)
            while True:
                try:
                    conn, addr = self.server_socket.accept()
                    t = threading.Thread(
                        target=self.handle_peer, args=(conn, addr)
                    )
                    t.daemon = True
                    t.start()
                except socket.timeout:
                    print("Waiting for a connection...")
        except KeyboardInterrupt:
            print("Shtting down the tracker...")
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

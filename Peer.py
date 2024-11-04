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


if __name__ == "__main__":
    peer_id = 1
    peer = Peer(peer_id)

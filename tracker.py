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

    def send_http_response(self, conn, status_code, content):
        """Send an HTTP response with a JSON payload"""
        status_messages = {
            200: "OK",
            400: "Bad request",
            500: "Internal Server Error",
        }
        status_message = status_messages.get(status_code, "OK")

        # Determine if the response should be JSON or plain text
        if isinstance(content, dict):
            # JSON response
            response_body = json.dumps(content)
            content_type = "application/json"
        else:
            # Plain text response
            response_body = content
            content_type = "text/plain"

        response = (
            f"HTTP/1.1 {status_code} {status_message}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{response_body}"
        )
        conn.sendall(response.encode())

    def register_peer(self, id, ip, port, bitfield):
        if id:
            self.peers[id] = {
                "ip": ip,
                "port": port,
                "bitfield": bitfield,
                "online": True,
            }
            print(
                f"Registered peer: {id} at {ip}:{port} with bitfield {bitfield}."
            )

    def handle_peer(self, conn, addr):
        """Handle individual peer connections."""
        try:
            request = conn.recv(CONFIGS["BUFFER_SIZE"]).decode()
            if request.startswith("GET"):
                self.handle_get_request(conn, request)
            elif request.startswith("PUT"):
                self.handle_put_request(conn, request)
            else:
                self.send_http_response(
                    conn, 400, {"error": "Unsupported request"}
                )
        except Exception as e:
            print(f"Error handling peer: {e}")
            self.send_http_response(
                conn, 500, {"error": "Internal Server Error"}
            )
        finally:
            conn.close()

    def handle_get_request(self, conn, request):
        """Process incoming requests from peers."""
        try:
            # Split request to parse GET parameters
            request_line = request.splitlines()[0]
            method, path, _ = request_line.split()

            # Ensure it's an HTTP GET request
            if method != "GET":
                self.send_http_response(conn, 400, {"error": "Bad Request"})
                return

            # Extract query parameters from the path
            query = path.split("?")[1]
            params = dict(item.split("=") for item in query.split("&"))

            # Retrieve necessary parameters
            peer_id = params.get("peer_id")
            peer_ip = params.get("peer_ip_address")
            peer_port = params.get("peer_port")
            bitfield = params.get("bitfield")
            # print(
            #     f"id: {peer_id}, ip: {peer_ip}, port: {peer_port}, bitfield: {bitfield}"
            # )

            # Check if any required parameters are missing
            if not peer_id or not peer_ip or not peer_port or not bitfield:
                self.send_http_response(
                    conn, 400, {"error": "Bad Request, missing parameters"}
                )
                return

            if "announce" in path:
                # Register the peer with extracted data
                self.register_peer(peer_id, peer_ip, peer_port, bitfield)

            peer_list_text = "\n".join(
                f"peer id: {id}, ip: {details['ip']}, port: {details['port']}, bitfield: {details['bitfield']}"
                for id, details in self.peers.items()
            )
            self.send_http_response(conn, 200, peer_list_text)

        except Exception as e:
            print(f"Error handling GET request: {e}")
            self.send_http_response(
                conn, 500, {"error": "Internal Server Error"}
            )

    def handle_put_request(self, conn, request):
        try:
            # Split request to parse PUT parameters
            request_line = request.splitlines()[0]
            method, path, _ = request_line.split()

            # Ensure it's an HTTP PUT request
            if method != "PUT":
                self.send_http_response(conn, 400, {"error": "Bad Request"})
                return

            # Extract query parameters from the path
            query = path.split("?")[1]
            params = dict(item.split("=") for item in query.split("&"))

            # Retrieve necessary parameters
            peer_id = params.get("peer_id")
            peer_ip = params.get("peer_ip_address")
            peer_port = params.get("peer_port")
            bitfield = params.get("bitfield")
            # print(
            #     f"id: {peer_id}, ip: {peer_ip}, port: {peer_port}, bitfield: {bitfield}"
            # )

            # Check if any required parameters are missing
            if not peer_id or not peer_ip or not peer_port or not bitfield:
                self.send_http_response(
                    conn, 400, {"error": "Bad Request, missing parameters"}
                )
                return

            if "seeding" in path:
                # Check if the peer is already registered
                if peer_id in self.peers:
                    # Update the peer's bitfield
                    self.peers[peer_id]["bitfield"] = bitfield
                    print(f"Updated bitfield for peer {peer_id} to {bitfield}")
                else:
                    # Peer is not found
                    self.send_http_response(
                        conn,
                        400,
                        {"error": "Peer not found, cannot update bitfield"},
                    )
                    return

            peer_list_text = "\n".join(
                f"peer id: {id}, ip: {details['ip']}, port: {details['port']}, bitfield: {details['bitfield']}"
                for id, details in self.peers.items()
            )
            self.send_http_response(conn, 200, peer_list_text)
        except Exception as e:
            print(f"Error handling PUT request: {e}")
            self.send_http_response(
                conn, 500, {"error": "Internal Server Error"}
            )

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

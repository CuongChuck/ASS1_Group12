import asyncio
import os

from config import CONFIGS


class Peer:
    def __init__(self):
        self.ip_address = "127.0.0.1"
        self.id = "123"
        self.port = 60000
        self.address = self.ip_address + ":" + str(self.port)
        self.bitfield = ["0", "0", "1", "1", "0", "0"]
        self.filename = ["", "", "piece_1.txt", "piece_2.txt", "", ""]
        self.downloaded_num = 0
        self.request_pieces = set()
        self.directory = f"files_{self.id}"
        # self.peer_list = [
        #    {"peer id": "123", "ip": "127.0.0.1", "port": 60000, "bitfield": "001100"},
        #    {"peer id": "456", "ip": "127.0.0.1", "port": 61000, "bitfield": "110010"},
        #    {"peer id": "789", "ip": "127.0.0.1", "port": 62000, "bitfield": "101001"}
        # ]
        self.peer_list = []

    async def connect_tracker(self):
        reader, writer = await asyncio.open_connection(
            CONFIGS["TRACKER_HOST"], CONFIGS["TRACKER_PORT"]
        )
        print(f"Peer {self.address} is connected to tracker")
        request = (
            f"GET /announce?peer_id={self.id}&peer_ip_address={self.ip_address}&peer_port={self.port}&bitfield={''.join(self.bitfield)} HTTP/1.1\r\n"
            f'Host: {CONFIGS["TRACKER_HOST"]}:{CONFIGS["TRACKER_PORT"]}\r\n'
            "Connection: close\r\n"
            "\r\n"
        )
        writer.write(request.encode())
        await writer.drain()
        response = await reader.read(1500)
        writer.close()
        await writer.wait_closed()
        self.peer_list = self.parse_response(response.decode())

    def parse_response(self, response):
        peers = []
        lines = response.strip().split("\n")
        for line in lines:
            if line.startswith("peer id:"):
                parts = line.split(", ")
                peer_info = {}
                for part in parts:
                    key, value = part.split(": ", 1)
                    peer_info[key.strip()] = value.strip()
                peers.append(peer_info)
        return peers

    async def handle_connection(self):
        await self.connect_tracker()
        task = asyncio.create_task(self.listen_peers())
        await asyncio.sleep(10)
        await self.connect_peers()
        await asyncio.sleep(30)
        task.cancel()

    async def listen_peer(self, reader, writer):
        source_address = writer.get_extra_info("peername")
        print(f"[{self.address}] Waiting for request from {source_address}")
        request = await reader.read(1500)
        print(f"[{self.address}] Request received from {source_address}")
        request = request.decode()
        lines = request.split("\r\n")
        for line in lines:
            if line.startswith("GET"):
                parse_1 = line.split(" ")
                for raw_info in parse_1:
                    if raw_info.startswith("/download"):
                        infos = raw_info.split("&")
                        for info in infos:
                            if info.startswith("piece="):
                                idx = info.index("=")
                                piece_num = int(info[(idx + 1) :])
                                filepath = os.path.join(
                                    self.directory, self.filename[piece_num]
                                )
                                with open(filepath, "r") as infile:
                                    data = infile.read()
                                    response = (
                                        "HTTP/1.1 200 OK\r\n"
                                        "Content-Type: text/plain; charset=utf-8\r\n"
                                        f"Content-Length: {len(data)}\r\n"
                                        "Connection: close\r\n"
                                        "\r\n"
                                        f"{data}"
                                    )
                                    print(
                                        f"[{self.address}] Sending response to {source_address}"
                                    )
                                    writer.write(response.encode())
                                    await writer.drain()

        writer.close()

    async def listen_peers(self):
        server = await asyncio.start_server(
            self.listen_peer, self.ip_address, self.port
        )
        addr = server.sockets[0].getsockname()
        print(f"[{self.address}] Listening on {addr}")

        async with server:
            await server.serve_forever()

    async def connect_peers(self):
        tasks = []
        left = self.bitfield.count("0")
        while left > 0:
            for peer in self.peer_list:
                if peer["peer id"] != self.id:
                    for index in range(len(peer["bitfield"])):
                        if (
                            (index not in self.request_pieces)
                            and peer["bitfield"][index] == "1"
                            and self.bitfield[index] == "0"
                        ):
                            self.request_pieces.add(index)
                            task = asyncio.create_task(
                                self.connect_peer(
                                    peer["ip"], peer["port"], index
                                )
                            )
                            left -= 1
                            tasks.append(task)

        await asyncio.gather(*tasks)

    async def connect_peer(self, ip, port, piece):
        destination_address = f"{ip}:{port}"
        reader, writer = await asyncio.open_connection(ip, port)
        print(
            f"[{self.address}] Connected to {destination_address} and ready to make a request"
        )
        request = (
            f"GET /download?peer_id={self.id}&peer_ip_address={self.ip_address}&peer_port={self.port}&piece={piece} HTTP/1.1\r\n"
            f"Host: {destination_address}\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        writer.write(request.encode())
        await writer.drain()
        print(f"[{self.address}] Sending a request to {destination_address}")
        response = await reader.read(1500)
        print(
            f"[{self.address}] Received a response from {destination_address}"
        )
        res = response.decode()
        data = res.split("\r\n")[-1]
        if data:
            filename = f"downloaded_piece_{self.downloaded_num}.txt"
            filepath = os.path.join(self.directory, filename)
            self.downloaded_num += 1
            with open(filepath, "w") as outfile:
                outfile.write(data)
            print(f"[{self.address}] Downloaded piece {piece} as {filename}")
            self.bitfield[piece] = "1"
            self.filename[piece] = filename
            await self.seeding()
            self.check_and_combine()

        writer.close()

    def check_and_combine(self):
        if (
            self.bitfield[0] == "1"
            and self.bitfield[1] == "1"
            and self.bitfield[2] == "1"
        ):
            filename = "file_1.txt"
            filepath = os.path.join(self.directory, filename)
            print(f"[{self.address}] Combining pieces of file 1")
            with open(filepath, "w") as outfile:
                for index in range(3):
                    infilepath = os.path.join(
                        self.directory, self.filename[index]
                    )
                    with open(infilepath, "r") as infile:
                        data = infile.read()
                        outfile.write(data)

            print(f"[{self.address}] Combined pieces of file 1 into file_1.txt")

        if (
            self.bitfield[3] == "1"
            and self.bitfield[4] == "1"
            and self.bitfield[5] == "1"
        ):
            filename = "file_2.txt"
            filepath = os.path.join(self.directory, filename)
            print(f"[{self.address}] Combining pieces of file 2")
            with open(filepath, "w") as outfile:
                for index in range(3, 6):
                    infilepath = os.path.join(
                        self.directory, self.filename[index]
                    )
                    with open(infilepath, "r") as infile:
                        data = infile.read()
                        outfile.write(data)

            print(f"[{self.address}] Combined pieces of file 2 into file_2.txt")

    async def seeding(self):
        reader, writer = await asyncio.open_connection(
            CONFIGS["TRACKER_HOST"], CONFIGS["TRACKER_PORT"]
        )
        print(f"[{self.address}] Connected to tracker")
        request = (
            f"PUT /seeding?peer_id={self.id}&peer_ip_address={self.ip_address}&peer_port={self.port}&bitfield={''.join(self.bitfield)} HTTP/1.1\r\n"
            f'Host: {CONFIGS["TRACKER_HOST"]}:{CONFIGS["TRACKER_PORT"]}\r\n'
            "Connection: close\r\n"
            "\r\n"
        )
        writer.write(request.encode())
        await writer.drain()
        response = await reader.read(1500)
        writer.close()
        await writer.wait_closed()
        self.peer_list = self.parse_response(response.decode())


if __name__ == "__main__":
    peer = Peer()
    asyncio.run(peer.handle_connection())

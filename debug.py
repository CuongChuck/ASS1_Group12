import json

peer_list = [
    {
        "id": "123",
        "ip": "127.0.0.1",
        "port": "8888",
        "bitfield": ["0", "1", "1", "0", "1", "0"],
    }
]
print(len(json.dumps(peer_list)))

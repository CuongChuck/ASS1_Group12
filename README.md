# STA

Build a Simple Torrent-like Application (STA) with the protocols defined by each group, using the TCP/IP protocol stack and must support multi-direction data transfering (MDDT).

## Specification

### Tracker

-   Tracker can run a server on localhost

### Peer

-   Peer can connect to server

## API

### `GET /`

Peer sends a `GET` request to `/` and receives the response as follows.

```python
request = (
    f"GET /?peer_id={peer.id}&peer_ip_address={peer.ip_address}&peer_port={peer.port}&bitfield={peer.bitfield} HTTP/1.1\r\n"
    "Host: 127.0.0.1:8888\r\n"
    "User-Agent: CustomClient/1.0\r\n"
    "Connection: close\r\n"
    "\r\n"
)
```

```python
response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: 94\r\n"
    "Connection: close\r\n"
    "\r\n"
    '[{"id":"123","ip":"127.0.0.1","port":"8888","bitfield":["0","1","1","0","1","0"]}]'
)
```

### `GET /announce`

Peer sends a `GET` request to `/announce`, tracker adds peer to peer list and send the response as follows.

```python
request = (
    f"GET /announce?peer_id={peer.id}&peer_ip_address={peer.ip_address}&peer_port={peer.port}&bitfield={peer.bitfield} HTTP/1.1\r\n"
    "Host: 127.0.0.1:8888\r\n"
    "User-Agent: CustomClient/1.0\r\n"
    "Connection: close\r\n"
    "\r\n"
)
```

```python
response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: 94\r\n"
    "Connection: close\r\n"
    "\r\n"
    '[{"id":"123","ip":"127.0.0.1","port":"8888","bitfield":["0","1","1","0","1","0"]}]'
)
```

### `PUT /seeding`

Peer sends a `PUT` request to `/seeding` to update `bitfield` and receives the response as follows.

```python
request = (
    f"PUT /seeding?peer_id={peer.id}&peer_ip_address={peer.ip_address}&peer_port={peer.port}&bitfield={peer.bitfield} HTTP/1.1\r\n"
    "Host: 127.0.0.1:8888\r\n"
    "User-Agent: CustomClient/1.0\r\n"
    "Connection: close\r\n"
    "\r\n"
)
```

```python
response = (
    "HTTP/1.1 200 OK\r\n"
    "Content-Type: application/json\r\n"
    "Content-Length: 94\r\n"
    "Connection: close\r\n"
    "\r\n"
    '[{"id":"123","ip":"127.0.0.1","port":"8888","bitfield":["0","1","0","0","1","0"]}]'
)
```

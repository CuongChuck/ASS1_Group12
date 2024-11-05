# STA

Build a Simple Torrent-like Application (STA) with the protocols defined by each group, using the TCP/IP protocol stack and must support multi-direction data transfering (MDDT).

## Specification

### Tracker

-   Tracker can run a server on localhost

### Peer

-   Peer can connect to server

## API

### `GET /announce`

```python
request = (
    f"GET /announce?peer_id={peer.id}&peer_ip_address={peer.ip_address}&peer_port={peer.port}&bitfield={peer.bitfield} HTTP/1.1\r\n"
    "Host: 127.0.0.1:8888\r\n"
    "User-Agent: CustomClient/1.0\r\n"
    "Connection: close\r\n"
    "\r\n"
)
```

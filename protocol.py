import json
import struct


PACKET_FILE_START = "FILE_START"
PACKET_FILE_CHUNK = "FILE_CHUNK"
PACKET_FILE_END = "FILE_END"


def recv_exact(sock, n):
    data = b""

    while len(data) < n:
        chunk = sock.recv(n - len(data))

        if not chunk:
            raise ConnectionError("Conexiunea s-a inchis.")

        data += chunk

    return data


def send_packet(sock, packet_type, payload: bytes):
    """
    Format pachet:
    [4 bytes header_len][header_json][4 bytes payload_len][payload]
    """

    header = {
        "type": packet_type
    }

    header_bytes = json.dumps(header).encode("utf-8")

    sock.sendall(struct.pack(">I", len(header_bytes)))
    sock.sendall(header_bytes)

    sock.sendall(struct.pack(">I", len(payload)))
    sock.sendall(payload)


def receive_packet(sock):
    """
    Returneaza:
    packet_type, payload
    """

    raw_header_len = recv_exact(sock, 4)
    header_len = struct.unpack(">I", raw_header_len)[0]

    header_bytes = recv_exact(sock, header_len)
    header = json.loads(header_bytes.decode("utf-8"))

    raw_payload_len = recv_exact(sock, 4)
    payload_len = struct.unpack(">I", raw_payload_len)[0]

    payload = recv_exact(sock, payload_len)

    return header["type"], payload
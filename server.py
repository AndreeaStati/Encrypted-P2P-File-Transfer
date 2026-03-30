import socket
import struct
import threading
from blowfish import decrypt_message, encrypt_message

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Conexiunea s-a închis.")
        data += chunk
    return data

def recv_message(sock):
    raw_len = recv_exact(sock, 4)
    msg_len = struct.unpack('>I', raw_len)[0]
    return recv_exact(sock, msg_len).decode('utf-8')

def send_message(sock, plaintext, p, s):
    encrypted = encrypt_message(plaintext, p, s)
    encoded = encrypted.encode('utf-8')
    sock.sendall(struct.pack('>I', len(encoded)) + encoded)

def handle_incoming(conn, addr, p, s):
    print(f"\n[SERVER] (+) Conexiune de la {addr[0]}:{addr[1]}")
    try:
        while True:
            encrypted_msg = recv_message(conn)
            print(f"\n[SERVER] [← CRIPTAT]   {encrypted_msg[:60]}...")
            plaintext = decrypt_message(encrypted_msg, p, s)
            print(f"[SERVER] [← DECRIPTAT] {plaintext}")
    except ConnectionError:
        print(f"[SERVER] (-) {addr[0]} deconectat.")
    finally:
        conn.close()

def start_server(port, p, s):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(10)
    print(f"[SERVER] (*) Ascultă pe portul {port}...")

    while True:
        conn, addr = srv.accept()
        t = threading.Thread(
            target=handle_incoming,
            args=(conn, addr, p, s),
            daemon=True
        )
        t.start()
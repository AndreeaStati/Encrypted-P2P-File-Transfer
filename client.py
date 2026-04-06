import socket
import struct
import time
from blowfish import encrypt_message, decrypt_message

def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Conexiunea s-a inchis.")
        data += chunk
    return data

def recv_message(sock):
    raw_len = recv_exact(sock, 4)
    msg_len = struct.unpack('>I', raw_len)[0]
    return recv_exact(sock, msg_len).decode('utf-8')

def send_message(sock, plaintext, p, s):
    encrypted = encrypt_message(plaintext, p, s)
    print(f"[CLIENT] [→ PLAINTEXT] {plaintext}")
    print(f"[CLIENT] [→ CRIPTAT]   {encrypted[:60]}...")
    encoded = encrypted.encode('utf-8')
    sock.sendall(struct.pack('>I', len(encoded)) + encoded)

def connect_to_peer(peer, p, s, connections, lock):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer["ip"], peer["port"]))
            with lock:
                connections[peer["name"]] = sock
            print(f"[CLIENT] (+) Conectat la {peer['name']} ({peer['ip']}:{peer['port']})")
            return
        except ConnectionRefusedError:
            print(f"[CLIENT] (~) {peer['name']} indisponibil ...")
            time.sleep(3)

def send_to(peer_name, message, my_name, connections, lock, p, s):
    with lock:
        sock = connections.get(peer_name)
    if not sock:
        print(f"[CLIENT] (!) {peer_name} nu e conectat.")
        return
    send_message(sock, f"[{my_name}] {message}", p, s)

def send_to_all(message, my_name, connections, lock, p, s):
    with lock:
        names = list(connections.keys())
    for name in names:
        send_to(name, message, my_name, connections, lock, p, s)
import socket
import struct
import time
from blowfish import encrypt_message, decrypt_message, expand_key 
from p2p_utils import send_data_chunked
import diffie_hellman 

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
    from blowfish import encrypt_message
    print(f"[CLIENT] [→ ORIGINAL] {plaintext[:50]}...")
    
    encrypted = encrypt_message(plaintext, p, s)
    encoded = encrypted.encode('utf-8')
    
    import struct
    sock.sendall(struct.pack('>I', len(encoded)) + encoded)
    
    print(f"[CLIENT] [--> STATUS] Mesaj trimis cu succes.")


def connect_to_peer(peer, connections, lock):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((peer["ip"], peer["port"]))
            
            # --- INCEPUT SCHIMB DIFFIE-HELLMAN (Partea de Client) ---
            print(f"[CLIENT] Conectat la {peer['name']}. Incep negocierea DH...")
            
            # 1. Generez cheile mele
            my_private, my_public = diffie_hellman.generate_keypair()
            
            # 2. Trimit cheia mea publica la server
            sock.send(str(my_public).encode('utf-8'))
            
            # 3. Primesc cheia publica a serverului
            server_pub_str = sock.recv(4096).decode('utf-8')
            server_public = int(server_pub_str)
            
            # 4. Calculez cheia Blowfish
            blowfish_key = diffie_hellman.calculate_blowfish_key(my_private, server_public)
            print(f"[CLIENT] Cheie negociata cu succes cu {peer['name']}.")
            
            # 5. Expandez cheia in matricile specifice acestui peer
            p, s = expand_key(blowfish_key)
            # --- SFARSIT SCHIMB DIFFIE-HELLMAN ---
            
            with lock:
                connections[peer["name"]] = {
                    "socket": sock,
                    "p": p,
                    "s": s
                }
            print(f"[CLIENT] (+) Gata de transmis date catre {peer['name']} ({peer['ip']}:{peer['port']})")
            return
        except ConnectionRefusedError:
            print(f"[CLIENT] (~) {peer['name']} indisponibil ...")
            time.sleep(3)

def send_to(peer_name, message, my_name, connections, lock):
    with lock:
        peer_data = connections.get(peer_name)
        
    if not peer_data:
        print(f"[CLIENT] (!) {peer_name} nu e conectat.")
        return
        
    sock = peer_data["socket"]
    p = peer_data["p"]
    s = peer_data["s"]
    
    send_message(sock, f"[{my_name}] {message}", p, s)

def send_to_all(message, my_name, connections, lock):
    with lock:
        names = list(connections.keys())
    for name in names:
        send_to(name, message, my_name, connections, lock)
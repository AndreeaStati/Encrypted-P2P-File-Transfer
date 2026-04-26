import socket
import struct
import threading
from blowfish import decrypt_message, encrypt_message

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
    encoded = encrypted.encode('utf-8')
    sock.sendall(struct.pack('>I', len(encoded)) + encoded)
from p2p_utils import receive_data_reconstructed
def handle_incoming(conn, addr, p, s):
    from blowfish import decrypt_message
    from p2p_utils import receive_data_reconstructed, handle_file_reception, recv_exact
    
    try:
        while True:
            # Citim lungimea primului pachet
            raw_len = recv_exact(conn, 4)
            msg_len = struct.unpack('>I', raw_len)[0]
            data = recv_exact(conn, msg_len).decode('utf-8')

            # Verificăm dacă este metadata de fișier
            if data.startswith("FILE_METADATA:"):
                handle_file_reception(conn, p, s, decrypt_message, data)
            else:
                # Dacă nu e fișier, e un mesaj normal (dar trebuie să-l tratăm ca segmentat)
                # Notă: Aici va trebui să ajustezi puțin logica pentru a nu citi lungimea de două ori
                # O soluție simplă este să trimiți mereu un header de tip [TIP_MESAJ] înainte.
                print(f"\n[SERVER] [MESAJ] {data}")
    except:
        conn.close()
        
def start_server(port, p, s):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(10)
    print(f"[SERVER] (*) Asculta pe portul {port}...")

    while True:
        conn, addr = srv.accept()
        t = threading.Thread(
            target=handle_incoming,
            args=(conn, addr, p, s),
            daemon=True
        )
        t.start()
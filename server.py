import socket
import struct
import threading
from blowfish import decrypt_message, encrypt_message, expand_key 
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
    encrypted = encrypt_message(plaintext, p, s)
    encoded = encrypted.encode('utf-8')
    sock.sendall(struct.pack('>I', len(encoded)) + encoded)

def handle_incoming(conn, addr, p, s):
    from p2p_utils import receive_data_reconstructed, handle_file_reception
    from blowfish import decrypt_message
    
    try:
        while True:
            raw_len = recv_exact(conn, 4)
            msg_len = struct.unpack('>I', raw_len)[0]
            data = recv_exact(conn, msg_len).decode('utf-8')

            if data.startswith("FILE_METADATA:"):
                handle_file_reception(conn, p, s, decrypt_message, data)
            else:
                try:
                    
                    text_clar = decrypt_message(data, p, s)
                    print(f"\n[SERVER] [MESAJ DECRIPTAT] {text_clar}")
                except Exception as e:
                    print(f"\n[SERVER] [MESAJ CRIPTAT] {data} (Eroare decriptare: {e})")
                    
    except Exception as e:
        print(f"[SERVER] Conexiunea cu {addr} s-a inchis.")
        conn.close()
        
def start_server(port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('0.0.0.0', port))
    srv.listen(10)
    print(f"[SERVER] (*) Asculta pe portul {port}...")

    while True:
        conn, addr = srv.accept()
        print(f"[SERVER] Conexiune acceptata de la {addr}. Incep negocierea DH...")
        
        # --- INCEPUT SCHIMB DIFFIE-HELLMAN  ---
        try:
            # 1. Primim cheia publica de la client (max 4096 bytes)
            client_pub_str = conn.recv(4096).decode('utf-8')
            client_public = int(client_pub_str)
            
            # 2. Generam cheile serverului
            my_private, my_public = diffie_hellman.generate_keypair()
            
            # 3. Trimitem cheia publica a serverului la client
            conn.send(str(my_public).encode('utf-8'))
            
            # 4. Calculam cheia finala de Blowfish
            blowfish_key = diffie_hellman.calculate_blowfish_key(my_private, client_public)
            print(f"[SERVER] Cheie stabilita cu {addr}.")
            
            # 5. Expandam cheia din bytes in matricile p si s
            p, s = expand_key(blowfish_key)
            
            t = threading.Thread(
                target=handle_incoming,
                args=(conn, addr, p, s),
                daemon=True
            )
            t.start()
        except Exception as e:
            print(f"[SERVER] Eroare la negocierea cheii cu {addr}: {e}")
            conn.close()
        # --- SFARSIT SCHIMB DIFFIE-HELLMAN ---
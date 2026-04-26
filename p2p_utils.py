import struct
import os
def recv_exact(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk: raise ConnectionError("Conexiune închisă.")
        data += chunk
    return data

def send_data_chunked(sock, data_bytes, p, s, encrypt_func, block_size=1024):
    total_size = len(data_bytes)
    #trimitem dim totala 4 bytes
    sock.sendall(struct.pack('>I', total_size))
    
    #trimitem datele in chunks
    for i in range(0, total_size, block_size):
        chunk = data_bytes[i:i + block_size]
        
        #criptare chunk folosind blowfish.py
        #Nota: encrypt_message face deja padding și base64
        encrypted_chunk = encrypt_func(chunk.decode('utf-8', errors='ignore'), p, s)
        encoded_chunk = encrypted_chunk.encode('utf-8')
        
        #trimitem dim frag criptat + fragment
        sock.sendall(struct.pack('>I', len(encoded_chunk)) + encoded_chunk)

def receive_data_reconstructed(sock, p, s, decrypt_func):
    #citim dim totala pe care trebuie să o aibă mesajul final
    raw_total_size = recv_exact(sock, 4)
    total_expected = struct.unpack('>I', raw_total_size)[0]
    
    reconstructed_message = ""
    current_size = 0
    
    #primim frag pana cand am recompus tot mesajul
    while current_size < total_expected:
        raw_seg_len = recv_exact(sock, 4)
        seg_len = struct.unpack('>I', raw_seg_len)[0]
        
        encrypted_seg = recv_exact(sock, seg_len).decode('utf-8')
        decrypted_seg = decrypt_func(encrypted_seg, p, s)
        
        reconstructed_message += decrypted_seg
        current_size = len(reconstructed_message.encode('utf-8'))
        
    return reconstructed_message

def send_file_segmented(sock, file_path, p, s, encrypt_func):
    if not os.path.exists(file_path):
        print(f"[ERROR] Fișierul {file_path} nu există.")
        return

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    #trimitem un "pachet de control" (Metadata)
    #format: FILE_FLAG | NUME_FISIER | DIMENSIUNE
    header = f"FILE_METADATA:{file_name}:{file_size}"
    sock.sendall(struct.pack('>I', len(header.encode())) + header.encode())

    #trimitem continutul fisierului folosind logica de segmentare
    with open(file_path, 'rb') as f:
        data = f.read()
        #refolosim functia de segmentare existenta (care trimite lungimea totala + chunk-uri)
        send_data_chunked(sock, data, p, s, encrypt_func)
    
    print(f"[CLIENT] Fisierul '{file_name}' a fost trimis cu succes.")

def handle_file_reception(sock, p, s, decrypt_func, metadata):
    #metadata format: "FILE_METADATA:nume:dimensiune"
    _, file_name, file_size = metadata.split(":")
    print(f"[SERVER] Se primeste fisierul: {file_name} ({file_size} bytes)")

    #recompunem datele 
    file_data = receive_data_reconstructed(sock, p, s, decrypt_func)

    output_path = f"primit_{file_name}"
    with open(output_path, 'wb') as f:
        f.write(file_data.encode('utf-8') if isinstance(file_data, str) else file_data)
    
    print(f"[SERVER] Fisier salvat ca: {output_path}")
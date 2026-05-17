import struct
import os


def recv_exact(sock, n):
    data = b''

    while len(data) < n:
        chunk = sock.recv(n - len(data))

        if not chunk:
            raise ConnectionError("Conexiune inchisa.")

        data += chunk

    return data


def send_data_chunked(sock, data_bytes, p, s, encrypt_bytes_func, block_size=4096):
    total_size = len(data_bytes)

    # trimitem dimensiunea originala a fisierului
    sock.sendall(struct.pack(">I", total_size))

    for i in range(0, total_size, block_size):
        chunk = data_bytes[i:i + block_size]

        encrypted_chunk = encrypt_bytes_func(chunk, p, s)

        # trimitem dimensiunea bucatii criptate + bucata criptat
        sock.sendall(struct.pack(">I", len(encrypted_chunk)))
        sock.sendall(encrypted_chunk)


def receive_data_reconstructed(sock, p, s, decrypt_bytes_func):
    raw_total_size = recv_exact(sock, 4)
    total_expected = struct.unpack(">I", raw_total_size)[0]

    reconstructed_data = bytearray()

    while len(reconstructed_data) < total_expected:
        raw_seg_len = recv_exact(sock, 4)
        seg_len = struct.unpack(">I", raw_seg_len)[0]

        encrypted_seg = recv_exact(sock, seg_len)
        decrypted_seg = decrypt_bytes_func(encrypted_seg, p, s)

        reconstructed_data.extend(decrypted_seg)

    # taiem exact la dimensiunea initiala
    return bytes(reconstructed_data[:total_expected])


def send_file_segmented(sock, file_path, p, s, encrypt_bytes_func):
    if not os.path.exists(file_path):
        print(f"[ERROR] Fisierul {file_path} nu exista.")
        return

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    header = f"FILE_METADATA:{file_name}:{file_size}"
    header_bytes = header.encode("utf-8")

    sock.sendall(struct.pack(">I", len(header_bytes)))
    sock.sendall(header_bytes)

    with open(file_path, "rb") as f:
        data = f.read()

    send_data_chunked(sock, data, p, s, encrypt_bytes_func)

    print(f"[CLIENT] Fișierul '{file_name}' a fost trimis cu succes.")


def handle_file_reception(sock, p, s, decrypt_bytes_func, metadata):
    _, file_name, file_size = metadata.split(":")

    print(f"[SERVER] Se primeste fișierul: {file_name} ({file_size} bytes)")

    file_data = receive_data_reconstructed(sock, p, s, decrypt_bytes_func)

    output_path = f"primit_{file_name}"

    with open(output_path, "wb") as f:
        f.write(file_data)

    print(f"[SERVER] Fisier salvat ca: {output_path}")
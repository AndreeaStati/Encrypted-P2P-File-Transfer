import os
import json
import math

from protocol import (
    send_packet,
    receive_packet,
    PACKET_FILE_START,
    PACKET_FILE_CHUNK,
    PACKET_FILE_END
)


CHUNK_SIZE = 4096


def send_file_segmented(sock, file_path, p, s, encrypt_bytes_func):
    if not os.path.exists(file_path):
        print(f"[ERROR] Fisierul {file_path} nu exista.")
        return

    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    total_chunks = math.ceil(file_size / CHUNK_SIZE)

    metadata = {
        "file_name": file_name,
        "file_size": file_size,
        "chunk_size": CHUNK_SIZE,
        "total_chunks": total_chunks
    }

    send_packet(
        sock,
        PACKET_FILE_START,
        json.dumps(metadata).encode("utf-8")
    )

    print(f"[CLIENT] Incep trimiterea fisierului: {file_name}")
    print(f"[CLIENT] Dimensiune: {file_size} bytes")
    print(f"[CLIENT] Total pachete: {total_chunks}")

    chunk_index = 0

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)

            if not chunk:
                break

            encrypted_chunk = encrypt_bytes_func(chunk, p, s)

            chunk_payload = {
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "encrypted_data": encrypted_chunk.hex()
            }

            send_packet(
                sock,
                PACKET_FILE_CHUNK,
                json.dumps(chunk_payload).encode("utf-8")
            )

            print(f"[CLIENT] Pachet trimis: {chunk_index + 1}/{total_chunks}")

            chunk_index += 1

    end_payload = {
        "file_name": file_name,
        "total_chunks": total_chunks
    }

    send_packet(
        sock,
        PACKET_FILE_END,
        json.dumps(end_payload).encode("utf-8")
    )

    print(f"[CLIENT] Fisierul '{file_name}' a fost trimis cu succes.")


def handle_file_reception(sock, p, s, decrypt_bytes_func, first_payload):
    metadata = json.loads(first_payload.decode("utf-8"))

    file_name = metadata["file_name"]
    file_size = metadata["file_size"]
    total_chunks = metadata["total_chunks"]

    output_path = f"primit_{file_name}"

    print(f"[SERVER] Incep primirea fisierului: {file_name}")
    print(f"[SERVER] Dimensiune asteptata: {file_size} bytes")
    print(f"[SERVER] Total pachete asteptate: {total_chunks}")

    received_chunks = 0

    with open(output_path, "wb") as f:
        while True:
            packet_type, payload = receive_packet(sock)

            if packet_type == PACKET_FILE_CHUNK:
                chunk_info = json.loads(payload.decode("utf-8"))

                chunk_index = chunk_info["chunk_index"]
                encrypted_data = bytes.fromhex(chunk_info["encrypted_data"])

                decrypted_chunk = decrypt_bytes_func(encrypted_data, p, s)

                f.write(decrypted_chunk)

                received_chunks += 1

                print(
                    f"[SERVER] Pachet primit: "
                    f"{chunk_index + 1}/{total_chunks}"
                )

            elif packet_type == PACKET_FILE_END:
                print(f"[SERVER] Transfer finalizat pentru: {file_name}")
                break

    final_size = os.path.getsize(output_path)

    if final_size == file_size:
        print(f"[SERVER] Fisier salvat corect ca: {output_path}")
    else:
        print(
            f"[SERVER] Atentie: dimensiune diferita. "
            f"Asteptat {file_size}, primit {final_size} bytes."
        )
import base64
import os
from constants import P_INIT, S_INIT

def str_to_bytes(text):
    return text.encode("utf-8")

def bytes_to_str(data):
    return data.decode("utf-8")

BLOCK_SIZE = 8


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def pad_data(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([pad_len] * pad_len)


def unpad_data(data: bytes) -> bytes:
    if not data:
        raise ValueError("Date goale la eliminarea padding-ului.")

    pad_len = data[-1]

    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Padding invalid.")

    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Padding invalid.")

    return data[:-pad_len]


def encrypt_block_bytes(block: bytes, p, s) -> bytes:
    block_int = int.from_bytes(block, "big")
    encrypted_int = encrypt_block(block_int, p, s)
    return encrypted_int.to_bytes(BLOCK_SIZE, "big")


def decrypt_block_bytes(block: bytes, p, s) -> bytes:
    block_int = int.from_bytes(block, "big")
    decrypted_int = decrypt_block(block_int, p, s)
    return decrypted_int.to_bytes(BLOCK_SIZE, "big")

def calculate(L, s):
    a = (L >> 24) & 0xff
    b = (L >> 16) & 0xff
    c = (L >> 8) & 0xff
    d = L & 0xff
    
    temp = (s[0][a] + s[1][b]) & 0xffffffff
    temp = (temp ^ s[2][c]) & 0xffffffff
    temp = (temp + s[3][d]) & 0xffffffff
    return temp

def encrypt_block(data_64bit, p, s):
    L = (data_64bit >> 32) & 0xffffffff
    R = data_64bit & 0xffffffff
    
    for i in range(16):
        L = L ^ p[i]
        R = calculate(L,s) ^ R
        L, R = R, L  
        
    L, R = R, L  
    R = R ^ p[16]
    L = L ^ p[17]
    return (L << 32) | R

def decrypt_block(data_64bit, p, s):
    L = (data_64bit >> 32) & 0xffffffff
    R = data_64bit & 0xffffffff
    
    for i in range(17, 1, -1):
        L = L ^ p[i]
        R = calculate(L,s) ^ R
        L, R = R, L
        
    L, R = R, L 
    
    R = R ^ p[1]
    L = L ^ p[0]
    
    return (L << 32) | R

def expand_key(key_bytes):
    if not (4 <= len(key_bytes) <= 56):
        raise ValueError("Cheia Blowfish trebuie sa aiba intre 4 si 56 bytes.")

    p = list(P_INIT)
    s = [list(box) for box in S_INIT]

    key_index = 0

    for i in range(18):
        word = 0
        for _ in range(4):
            word = ((word << 8) | key_bytes[key_index]) & 0xffffffff
            key_index = (key_index + 1) % len(key_bytes)
        p[i] ^= word

    block = 0

    for i in range(0, 18, 2):
        block = encrypt_block(block, p, s)
        p[i] = (block >> 32) & 0xffffffff
        p[i + 1] = block & 0xffffffff

    for i in range(4):
        for j in range(0, 256, 2):
            block = encrypt_block(block, p, s)
            s[i][j] = (block >> 32) & 0xffffffff
            s[i][j + 1] = block & 0xffffffff

    return p, s


def encrypt_bytes(data: bytes, p, s) -> bytes:
    """
    Criptare Blowfish in modul CBC.
    Returneaza: IV + ciphertext
    """
    iv = os.urandom(BLOCK_SIZE)
    padded_data = pad_data(data)

    encrypted = bytearray()
    encrypted.extend(iv)

    previous_block = iv

    for i in range(0, len(padded_data), BLOCK_SIZE):
        block = padded_data[i:i + BLOCK_SIZE]

        xored_block = xor_bytes(block, previous_block)
        encrypted_block = encrypt_block_bytes(xored_block, p, s)

        encrypted.extend(encrypted_block)

        previous_block = encrypted_block

    return bytes(encrypted)


def decrypt_bytes(encrypted_data: bytes, p, s) -> bytes:
    """
    Decriptare Blowfish in modul CBC.
    Primeste: IV + ciphertext
    """
    if len(encrypted_data) < BLOCK_SIZE * 2:
        raise ValueError("Datele criptate sunt prea scurte pentru CBC.")

    iv = encrypted_data[:BLOCK_SIZE]
    ciphertext = encrypted_data[BLOCK_SIZE:]

    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError("Ciphertext invalid: lungimea nu este multiplu de 8.")

    decrypted = bytearray()

    previous_block = iv

    for i in range(0, len(ciphertext), BLOCK_SIZE):
        encrypted_block = ciphertext[i:i + BLOCK_SIZE]

        decrypted_block = decrypt_block_bytes(encrypted_block, p, s)
        plain_block = xor_bytes(decrypted_block, previous_block)

        decrypted.extend(plain_block)

        previous_block = encrypted_block

    return unpad_data(bytes(decrypted))


def encrypt_message(message, p, s):
    data = str_to_bytes(message)

    encrypted_data = encrypt_bytes(data, p, s)

    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt_message(encrypted_b64, p, s):
    encrypted_data = base64.b64decode(encrypted_b64)

    decrypted_data = decrypt_bytes(encrypted_data, p, s)

    return bytes_to_str(decrypted_data)
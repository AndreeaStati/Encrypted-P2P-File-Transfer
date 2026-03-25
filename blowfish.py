import base64
from constants import P_INIT, S_INIT

def str_to_bytes(text):
    return text.encode("utf-8")

def bytes_to_str(data):
    return data.decode("utf-8")

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


def encrypt_message(message, p, s):
    data = str_to_bytes(message)

    pad_len = 8 - (len(data) % 8)
    data += bytes([pad_len] * pad_len)

    encrypted = bytearray()

    for i in range(0, len(data), 8):
        block = data[i:i + 8]
        block_int = int.from_bytes(block, "big")
        enc_block = encrypt_block(block_int, p, s)
        encrypted.extend(enc_block.to_bytes(8, "big"))

    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_message(encrypted_b64, p, s):
    data = base64.b64decode(encrypted_b64)

    if len(data) % 8 != 0:
        raise ValueError("Datele criptate au lungime invalida.")

    decrypted = bytearray()

    for i in range(0, len(data), 8):
        block = data[i:i + 8]
        block_int = int.from_bytes(block, "big")
        dec_block = decrypt_block(block_int, p, s)
        decrypted.extend(dec_block.to_bytes(8, "big"))

    pad_len = decrypted[-1]

    if pad_len < 1 or pad_len > 8:
        raise ValueError("Padding invalid.")

    if decrypted[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Padding invalid.")

    return bytes_to_str(decrypted[:-pad_len])
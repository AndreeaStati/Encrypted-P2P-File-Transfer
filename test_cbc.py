from blowfish import expand_key, encrypt_bytes, decrypt_bytes

key = b"testkey123"
p, s = expand_key(key)

message = b"Acesta este un test pentru Blowfish CBC."

encrypted = encrypt_bytes(message, p, s)
decrypted = decrypt_bytes(encrypted, p, s)

print("Original:", message)
print("Criptat:", encrypted.hex())
print("Decriptat:", decrypted)

assert decrypted == message

print("Test CBC reusit.")
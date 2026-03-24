from blowfish import expand_key, encrypt_message, decrypt_message

if __name__ == "__main__":
    #key_input = input("Enter key (4-56 chars): ")
    #key_bytes = key_input.encode("utf-8")
    
    key_bytes = b"mysecretkey"
    try:
        p, s = expand_key(key_bytes)
    except (TypeError, ValueError) as e:
        print(f"Eroare cheie: {e}")
        exit()

    input_str = input("Enter data to encrypt: ")

    try:
        data_encrypted = encrypt_message(input_str, p, s)
        print(f"Encrypted (Base64): {data_encrypted}")

        data_decrypted = decrypt_message(data_encrypted, p, s)
        print(f"Decrypted text: {data_decrypted}")
    except Exception as e:
        print(f"Eroare: {e}")
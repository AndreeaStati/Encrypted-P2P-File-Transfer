import unittest

from blowfish import (
    expand_key,
    encrypt_block,
    decrypt_block,
    encrypt_bytes,
    decrypt_bytes
)


class TestBlowfish(unittest.TestCase):

    def test_official_vector_1(self):
        key = bytes.fromhex("0000000000000000")
        plaintext = 0x0000000000000000
        expected_ciphertext = 0x4EF997456198DD78

        p, s = expand_key(key)

        result = encrypt_block(plaintext, p, s)

        self.assertEqual(result, expected_ciphertext)
        self.assertEqual(decrypt_block(result, p, s), plaintext)

    def test_official_vector_2(self):
        key = bytes.fromhex("FFFFFFFFFFFFFFFF")
        plaintext = 0xFFFFFFFFFFFFFFFF
        expected_ciphertext = 0x51866FD5B85ECB8A

        p, s = expand_key(key)

        result = encrypt_block(plaintext, p, s)

        self.assertEqual(result, expected_ciphertext)
        self.assertEqual(decrypt_block(result, p, s), plaintext)

    def test_official_vector_3(self):
        key = bytes.fromhex("3000000000000000")
        plaintext = 0x1000000000000001
        expected_ciphertext = 0x7D856F9A613063F2

        p, s = expand_key(key)

        result = encrypt_block(plaintext, p, s)

        self.assertEqual(result, expected_ciphertext)
        self.assertEqual(decrypt_block(result, p, s), plaintext)

    def test_cbc_encrypt_decrypt(self):
        key = b"testkey123"
        p, s = expand_key(key)

        original = b"Acesta este un test pentru Blowfish CBC."

        encrypted = encrypt_bytes(original, p, s)
        decrypted = decrypt_bytes(encrypted, p, s)

        self.assertEqual(decrypted, original)

    def test_cbc_iv_random(self):
        key = b"testkey123"
        p, s = expand_key(key)

        original = b"Mesaj identic pentru test IV."

        encrypted_1 = encrypt_bytes(original, p, s)
        encrypted_2 = encrypt_bytes(original, p, s)

        self.assertNotEqual(encrypted_1, encrypted_2)
        self.assertEqual(decrypt_bytes(encrypted_1, p, s), original)
        self.assertEqual(decrypt_bytes(encrypted_2, p, s), original)


if __name__ == "__main__":
    unittest.main()
import unittest

from blowfish import Blowfish

class TestBlowfishVectors(unittest.TestCase):
    def test_official_vector_1(self):
        # Vector oficial 1: Cheie de zero, date de zero
        # 0000000000000000 -> 4EF997456198DD78
        key = [0x00000000, 0x00000000] # 64 biti
        cipher = Blowfish(key)
        
        plaintext = 0x0000000000000000
        expected = 0x4EF997456198DD78
        
        result = cipher._encrypt_block(plaintext)
        self.assertEqual(result, expected, "Vectorul de test 1 a esuat!")

    def test_official_vector_2(self):
        # Vector oficial 2: Toți biții pe 1
        # FFFFFFFFFFFFFFFF -> 51866FD5B85ECB8A
        key = [0xFFFFFFFF, 0xFFFFFFFF]
        cipher = Blowfish(key)
        
        plaintext = 0xFFFFFFFFFFFFFFFF
        expected = 0x51866FD5B85ECB8A
        
        result = cipher._encrypt_block(plaintext)
        self.assertEqual(result, expected, "Vectorul de test 2 a esuat!")

    def test_symmetric_property(self):
        # Verificăm că encrypt + decrypt ne dă mesajul original
        key = [0x4B7A70E9, 0xB5B32944]
        cipher = Blowfish(key)
        
        original_message = "Acesta este un test pentru cursul de COM!"
        
        encrypted = cipher.encrypt(original_message)
        decrypted = cipher.decrypt(encrypted)
        
        self.assertEqual(original_message, decrypted, "Proprietatea simetrică a eșuat!")

    def test_padding_logic(self):
        # Mesaj fix 8 caractere (necesita fix un bloc de padding suplimentar)
        key = [0x12345678]
        cipher = Blowfish(key)
        
        text = "12345678" 
        encrypted = cipher.encrypt(text)
        decrypted = cipher.decrypt(encrypted)
        
        self.assertEqual(text, decrypted, "Logica de padding PKCS#7 a eșuat la limite de bloc!")

if __name__ == '__main__':
    unittest.main()
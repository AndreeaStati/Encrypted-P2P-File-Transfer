import unittest

from blowfish import Blowfish

class TestBlowfishVectors(unittest.TestCase):
    def test_official_vector_1(self):
       
        key = [0x00000000, 0x00000000] 
        cipher = Blowfish(key)
        
        plaintext = 0x0000000000000000
        expected = 0x4EF997456198DD78
        
        result = cipher._encrypt_block(plaintext)
        self.assertEqual(result, expected, "Vectorul de test 1 a esuat!")

    def test_official_vector_2(self):
      
        key = [0xFFFFFFFF, 0xFFFFFFFF]
        cipher = Blowfish(key)
        
        plaintext = 0xFFFFFFFFFFFFFFFF
        expected = 0x51866FD5B85ECB8A
        
        result = cipher._encrypt_block(plaintext)
        self.assertEqual(result, expected, "Vectorul de test 2 a esuat!")

    def test_symmetric_property(self):
        key = [0x4B7A70E9, 0xB5B32944]
        cipher = Blowfish(key)
        
        original_message = "Acesta este un test pentru cursul de COM!"
        
        encrypted = cipher.encrypt(original_message)
        decrypted = cipher.decrypt(encrypted)
        
        self.assertEqual(original_message, decrypted, "Proprietatea simetrica a esuat!")

    def test_padding_logic(self):
        key = [0x12345678]
        cipher = Blowfish(key)
        
        text = "12345678" 
        encrypted = cipher.encrypt(text)
        decrypted = cipher.decrypt(encrypted)
        
        self.assertEqual(text, decrypted, "Logica de padding PKCS#7 a esuat la limite de bloc!")

if __name__ == '__main__':
    unittest.main()
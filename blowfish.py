# blowfish.py
import base64
from constants import P_INIT, S_INIT

class Blowfish:
    def __init__(self, key_list):
        # Generăm sub-cheile specifice acestei instanțe prin Key Expansion
        self.p, self.s = self._expand_key(key_list)

    def _calculate(self, L, s_box=None):
        # Folosim self.s implicit, dar permitem s_box custom pentru expansiune
        current_s = s_box if s_box else self.s
        a, b, c, d = (L >> 24) & 0xff, (L >> 16) & 0xff, (L >> 8) & 0xff, L & 0xff
        temp = (current_s[0][a] + current_s[1][b]) & 0xffffffff
        temp = (temp ^ current_s[2][c]) & 0xffffffff
        return (temp + current_s[3][d]) & 0xffffffff

    def _encrypt_block(self, data_64bit, p_arr=None, s_box=None):
        current_p = p_arr if p_arr else self.p
        current_s = s_box if s_box else self.s
        
        L = (data_64bit >> 32) & 0xffffffff
        R = data_64bit & 0xffffffff
        
        for i in range(16):
            L ^= current_p[i]
            R ^= self._calculate(L, current_s)
            L, R = R, L
            
        L, R = R, L
        R ^= current_p[16]
        L ^= current_p[17]
        return (L << 32) | R

    def _decrypt_block(self, data_64bit):
        L = (data_64bit >> 32) & 0xffffffff
        R = data_64bit & 0xffffffff
        
        for i in range(17, 1, -1):
            L ^= self.p[i]
            R ^= self._calculate(L)
            L, R = R, L
            
        L, R = R, L
        R ^= self.p[1]
        L ^= self.p[0]
        return (L << 32) | R

    def _expand_key(self, key_list):
        p_working = list(P_INIT)
        s_working = [list(sub) for sub in S_INIT]
        
        # 1. XOR P-array cu cheia
        for i in range(18):
            p_working[i] ^= key_list[i % len(key_list)]
            
        # 2. Criptare succesivă pentru a genera noile sub-chei
        block = 0
        for i in range(0, 18, 2):
            block = self._encrypt_block(block, p_working, s_working)
            p_working[i] = (block >> 32) & 0xffffffff
            p_working[i+1] = block & 0xffffffff
            
        for i in range(4):
            for j in range(0, 256, 2):
                block = self._encrypt_block(block, p_working, s_working)
                s_working[i][j] = (block >> 32) & 0xffffffff
                s_working[i][j+1] = block & 0xffffffff
        return p_working, s_working

    def encrypt(self, message):
        data = message.encode('utf-8')
        pad_len = 8 - (len(data) % 8)
        data += bytes([pad_len] * pad_len)
        
        combined = bytearray()
        for i in range(0, len(data), 8):
            block_int = int.from_bytes(data[i:i+8], 'big')
            enc_block = self._encrypt_block(block_int)
            combined.extend(enc_block.to_bytes(8, 'big'))
            
        return base64.b64encode(combined).decode('utf-8')

    def decrypt(self, b64_string):
        data = base64.b64decode(b64_string)
        decrypted_data = bytearray()
        for i in range(0, len(data), 8):
            block_int = int.from_bytes(data[i:i+8], 'big')
            dec_block = self._decrypt_block(block_int)
            decrypted_data.extend(dec_block.to_bytes(8, 'big'))
        
        pad_len = decrypted_data[-1]
        return decrypted_data[:-pad_len].decode('utf-8')
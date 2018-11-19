import base64
import hashlib
import struct

from Crypto import Random
from Crypto.Cipher import AES
from django.conf import settings


class AESCipher(object):
    def __init__(self):
        self.bs = AES.block_size
        self.key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * '0'

    def encrypt(self, raw):
        raw_size = len(raw)
        raw_bytes = self._pad(raw)
        raw_size_bytes = struct.pack('<i', raw_size)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(
            iv + raw_size_bytes + cipher.encrypt(raw_bytes))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        raw_size = struct.unpack('<i', enc[self.bs:self.bs + 4])[0]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        raw_bytes = cipher.decrypt(enc[self.bs + 4:])
        raw = raw_bytes[:raw_size].decode('utf_8')
        return raw

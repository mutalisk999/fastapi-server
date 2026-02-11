#!/usr/bin/env python
# encoding: utf-8
import hashlib
import pyaes  # type: ignore


class Aes128Cbc(object):
    def __init__(self, key: bytes):
        hash_data = hashlib.sha256(key).digest()
        self.key = hash_data[0:16]
        self.iv = hash_data[16:32]

    def aes128_cbc_encrypt(self, plaintext: bytes) -> str:
        aes = pyaes.AESModeOfOperationCBC(self.key, self.iv)
        ciphertext = aes.encrypt(plaintext)
        return bytes.hex(ciphertext)

    def aes128_cbc_decrypt(self, ciphertext: str) -> str:
        aes = pyaes.AESModeOfOperationCBC(self.key, self.iv)
        ciphertext = bytes.fromhex(ciphertext)  # type: ignore
        plaintext = aes.decrypt(ciphertext)
        plaintext = plaintext.rstrip(b"\x00")
        return plaintext.decode("ascii")

#!/usr/bin/env python
# encoding: utf-8
import pyaes  # type: ignore


class Aes128Ctr(object):
    def __init__(self, key: bytes):
        self.key = key

    def aes128_ctr_encrypt(self, plaintext: bytes) -> str:
        key = self.key + b"\x00" * (16 - (len(self.key) % 16))
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = aes.encrypt(plaintext)
        return bytes.hex(ciphertext)

    def aes128_ctr_decrypt(self, ciphertext: str) -> str:
        key = self.key + b"\x00" * (16 - (len(self.key) % 16))
        aes = pyaes.AESModeOfOperationCTR(key)
        ciphertext = bytes.fromhex(ciphertext)  # type: ignore
        plaintext = aes.decrypt(ciphertext)
        plaintext = plaintext.rstrip(b"\x00")
        return plaintext.decode("ascii")

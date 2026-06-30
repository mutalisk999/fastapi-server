#!/usr/bin/env python
# encoding: utf-8
import hashlib
import pyaes  # type: ignore


class Aes128Cbc(object):
    def __init__(self, key: bytes):
        hash_data = hashlib.sha256(key).digest()
        self.key = hash_data[0:16]
        self.iv = hash_data[16:32]

    @staticmethod
    def _pkcs7_pad(data: bytes) -> bytes:
        pad_len = 16 - (len(data) % 16)
        return data + bytes([pad_len] * pad_len)

    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        pad_len = data[-1]
        return data[:-pad_len]

    def aes128_cbc_encrypt(self, plaintext: bytes) -> str:
        padded = self._pkcs7_pad(plaintext)
        ciphertext = b""
        for i in range(0, len(padded), 16):
            aes = pyaes.AESModeOfOperationCBC(self.key, self.iv)
            ciphertext += aes.encrypt(padded[i : i + 16])
        return bytes.hex(ciphertext)

    def aes128_cbc_decrypt(self, ciphertext: str) -> str:
        raw = bytes.fromhex(ciphertext)  # type: ignore
        plaintext = b""
        for i in range(0, len(raw), 16):
            aes = pyaes.AESModeOfOperationCBC(self.key, self.iv)
            plaintext += aes.decrypt(raw[i : i + 16])
        plaintext = self._pkcs7_unpad(plaintext)
        return plaintext.decode("utf-8")

#!/usr/bin/env python
# encoding: utf-8
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AesGcm(object):
    def __init__(self, key: bytes):
        # Derive a 256-bit key from the input key material
        self.key = hashlib.sha256(key).digest()

    def encrypt(self, plaintext: bytes) -> str:
        """Encrypt plaintext with AES-256-GCM. Returns hex-encoded nonce+ciphertext+tag."""
        aesgcm = AESGCM(self.key)
        nonce = os.urandom(12)  # 96-bit nonce is standard for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return (nonce + ciphertext).hex()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt hex-encoded nonce+ciphertext+tag with AES-256-GCM."""
        aesgcm = AESGCM(self.key)
        data = bytes.fromhex(ciphertext)
        nonce = data[:12]
        ciphertext_bytes = data[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext_bytes, None)
        return plaintext.decode("utf-8")


# Backward-compatible aliases
Aes128Cbc = AesGcm
aes128_cbc_encrypt = AesGcm.encrypt
aes128_cbc_decrypt = AesGcm.decrypt

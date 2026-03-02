#!/usr/bin/env python
# encoding: utf-8
import unittest
from utils.password_tools import password_tools


class TestPasswordTools(unittest.TestCase):
    """Test password tools"""
    
    def test_hash_password(self):
        """Test password hashing functionality"""
        password = "test_password"
        hashed_password = password_tools.hash_password(password)
        self.assertIsInstance(hashed_password, str)
        self.assertNotEqual(password, hashed_password)
    
    def test_verify_password(self):
        """Test password verification functionality"""
        password = "test_password"
        hashed_password = password_tools.hash_password(password)
        # Verify correct password
        self.assertTrue(password_tools.verify_password(password, hashed_password))
        # Verify wrong password
        self.assertFalse(password_tools.verify_password("wrong_password", hashed_password))


if __name__ == "__main__":
    unittest.main()
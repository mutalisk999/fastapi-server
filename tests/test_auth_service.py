#!/usr/bin/env python
# encoding: utf-8
import unittest
from services.auth_service import auth_service


class TestAuthService(unittest.TestCase):
    """Test authentication service"""
    
    def test_login(self):
        """Test login functionality"""
        # Test with correct username and password
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        result = auth_service.login(login_data["username"], login_data["password"])
        self.assertIn("access_token", result)
        self.assertIn("token_type", result)
        self.assertIn("expires_in", result)
        
        # Test with wrong password
        with self.assertRaises(ValueError):
            auth_service.login(login_data["username"], "wrong_password")
        
        # Test with wrong username
        with self.assertRaises(ValueError):
            auth_service.login("wrong_username", login_data["password"])
    
    def test_verify_token(self):
        """Test token verification functionality"""
        # First login to get token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_result = auth_service.login(login_data["username"], login_data["password"])
        token = login_result["access_token"]
        
        # Verify token
        verify_result = auth_service.verify_token(token)
        self.assertIsInstance(verify_result, dict)
        self.assertIn("user_id", verify_result)
        
        # Verify invalid token
        invalid_token = "invalid_token"
        verify_result = auth_service.verify_token(invalid_token)
        self.assertIsNone(verify_result)
    
    def test_refresh_token(self):
        """Test token refresh functionality"""
        import time
        
        # First login to get token
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_result = auth_service.login(login_data["username"], login_data["password"])
        token = login_result["access_token"]
        
        # Add a small delay to ensure timestamp is different
        time.sleep(0.1)
        
        # Refresh token
        refresh_result = auth_service.refresh_token(token)
        self.assertIn("access_token", refresh_result)
        self.assertIn("token_type", refresh_result)
        self.assertIn("expires_in", refresh_result)
        self.assertNotEqual(token, refresh_result["access_token"])


if __name__ == "__main__":
    unittest.main()
#!/usr/bin/env python
# encoding: utf-8
import unittest
from unittest.mock import patch, MagicMock
from services.auth_service import auth_service
from utils.authentication import auth_handler


class TestAuthService(unittest.TestCase):
    """Test authentication service"""

    def setUp(self):
        """Initialize auth_handler before each test"""
        auth_handler.initialize("test_secret_for_unit_tests_only")

    def test_login(self):
        """Test login functionality"""
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

    def test_login_without_init_raises(self):
        """Test that login raises RuntimeError when auth_handler is not initialized"""
        auth_handler.secret = None
        with self.assertRaises(RuntimeError):
            auth_service.login("admin", "admin123")
        # Restore for other tests
        auth_handler.initialize("test_secret_for_unit_tests_only")

    def test_verify_token(self):
        """Test token verification functionality"""
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

        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_result = auth_service.login(login_data["username"], login_data["password"])
        token = login_result["access_token"]

        # Wait enough for JWT timestamp to differ (iat is integer seconds)
        time.sleep(1.5)

        refresh_result = auth_service.refresh_token(token)
        self.assertIn("access_token", refresh_result)
        self.assertIn("token_type", refresh_result)
        self.assertIn("expires_in", refresh_result)
        self.assertNotEqual(token, refresh_result["access_token"])

    def test_logout(self):
        """Test logout functionality"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        login_result = auth_service.login(login_data["username"], login_data["password"])
        token = login_result["access_token"]

        # Logout should not raise
        auth_service.logout(token)


if __name__ == "__main__":
    unittest.main()

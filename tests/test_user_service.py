#!/usr/bin/env python
# encoding: utf-8
import unittest
from services.user_service import user_service


class TestUserService(unittest.TestCase):
    """测试用户服务"""
    
    def test_get_user_info(self):
        """测试获取用户信息功能"""
        user_id = "123"
        result = user_service.get_user_info(user_id)
        self.assertIsInstance(result, dict)
        self.assertIn("user_id", result)
        self.assertIn("username", result)
        self.assertIn("email", result)
        self.assertIn("created_at", result)
        self.assertEqual(result["user_id"], user_id)
    
    def test_create_user(self):
        """测试创建用户功能"""
        user_data = {
            "username": "test_user",
            "email": "test_user@example.com"
        }
        result = user_service.create_user(user_data)
        self.assertIsInstance(result, dict)
        self.assertIn("user_id", result)
        self.assertIn("username", result)
        self.assertIn("email", result)
        self.assertIn("created_at", result)
        self.assertEqual(result["username"], user_data["username"])
        self.assertEqual(result["email"], user_data["email"])
    
    def test_update_user(self):
        """测试更新用户功能"""
        user_id = "123"
        user_data = {
            "username": "updated_user",
            "email": "updated_user@example.com"
        }
        result = user_service.update_user(user_id, user_data)
        self.assertIsInstance(result, dict)
        self.assertIn("user_id", result)
        self.assertIn("username", result)
        self.assertIn("email", result)
        self.assertIn("updated_at", result)
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["username"], user_data["username"])
        self.assertEqual(result["email"], user_data["email"])
    
    def test_delete_user(self):
        """测试删除用户功能"""
        user_id = "123"
        result = user_service.delete_user(user_id)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
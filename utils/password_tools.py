#!/usr/bin/env python
# encoding: utf-8
import bcrypt
from utils.logger import logger


class PasswordTools:
    """Password tools class, for handling password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed_password.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        try:
            # Verify password
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False


# Create a global password tools instance
password_tools = PasswordTools()
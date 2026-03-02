#!/usr/bin/env python
# encoding: utf-8
from typing import Optional, Dict, Any
from utils.authentication import auth_handler
from utils.password_tools import password_tools
from utils.logger import logger


class AuthService:
    """Authentication service class, handling authentication-related business logic"""
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """User login"""
        try:
            # Initialize auth_handler if not already initialized
            if not auth_handler.secret:
                auth_handler.initialize("test_jwt_secret_key")
            
            # This should be the logic to get user information from the database
            # Temporarily return mock data
            if username == "admin":
                # Mock hashed password from database
                # Note: In actual application, this hashed password should be stored in the database
                hashed_password = "$2b$12$5yLWERchOfPdEQrZEiY93.F5NkYqLaVGaOu6D4umiWiBQW9rnx./a"
                # Verify password
                if password_tools.verify_password(password, hashed_password):
                    # Generate JWT token
                    token = auth_handler.generate_token(username)
                    return {
                        "access_token": token,
                        "token_type": "bearer",
                        "expires_in": 604800  # 7 days
                    }
                else:
                    raise ValueError("Invalid username or password")
            else:
                raise ValueError("Invalid username or password")
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token"""
        try:
            # Initialize auth_handler if not already initialized
            if not auth_handler.secret:
                auth_handler.initialize("test_jwt_secret_key")
            
            # Verify token
            payload = auth_handler.verify_token(token)
            if payload:
                return {
                    "user_id": payload.get("sub"),
                    "exp": payload.get("exp"),
                    "iat": payload.get("iat")
                }
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            raise
    
    def refresh_token(self, token: str) -> Dict[str, Any]:
        """Refresh token"""
        try:
            # Initialize auth_handler if not already initialized
            if not auth_handler.secret:
                auth_handler.initialize("test_jwt_secret_key")
            
            # Verify old token
            payload = auth_handler.verify_token(token)
            if not payload:
                raise ValueError("Invalid token")
            
            # Generate new token
            new_token = auth_handler.generate_token(payload.get("sub"))
            return {
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 604800  # 7 days
            }
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise


# Create a global authentication service instance
auth_service = AuthService()
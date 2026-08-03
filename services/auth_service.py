#!/usr/bin/env python
# encoding: utf-8
from typing import Optional, Dict, Any
from utils.authentication import auth_handler
from utils.password_tools import password_tools
from utils.logger import logger


class AuthService:
    """Authentication service class, handling authentication-related business logic"""
    
    def _ensure_initialized(self):
        """Ensure auth_handler is initialized, raise if not"""
        if not auth_handler.secret:
            raise RuntimeError("Auth handler not initialized - JWT secret is missing")

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """User login"""
        try:
            self._ensure_initialized()

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
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error during login: {e}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify token"""
        try:
            self._ensure_initialized()

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
            self._ensure_initialized()

            # Verify old token
            payload = auth_handler.verify_token(token)
            if not payload:
                raise ValueError("Invalid token")

            # Revoke the old token
            exp = payload.get("exp")
            if exp:
                from datetime import datetime, timezone
                remaining = exp - int(datetime.now(timezone.utc).timestamp())
                auth_handler.revoke_token(token, exp_seconds=max(remaining, 0))
            else:
                auth_handler.revoke_token(token)

            # Generate new token
            new_token = auth_handler.generate_token(payload.get("sub"))
            return {
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": 604800  # 7 days
            }
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            raise

    def logout(self, token: str):
        """Logout - revoke the token"""
        try:
            self._ensure_initialized()
            payload = auth_handler.decode_token(token)
            if payload:
                exp = payload.get("exp")
                if exp:
                    from datetime import datetime, timezone
                    remaining = exp - int(datetime.now(timezone.utc).timestamp())
                    auth_handler.revoke_token(token, exp_seconds=max(remaining, 0))
                else:
                    auth_handler.revoke_token(token)
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise


# Create a global authentication service instance
auth_service = AuthService()
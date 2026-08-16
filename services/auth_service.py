#!/usr/bin/env python
# encoding: utf-8
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from utils.authentication import auth_handler
from utils.password_tools import password_tools
from utils.logger import logger

# Token lifetime returned to clients. Must match the default expiration in
# AuthHandler.generate_token (86400 * 7).
TOKEN_EXPIRES_IN = 7 * 24 * 60 * 60  # 7 days


class AuthService:
    """Authentication service class, handling authentication-related business logic"""

    # DEV-ONLY mock credential. Plaintext is "admin123" - do NOT reuse in prod.
    # The login endpoint only accepts this while MOCK_AUTH_ENABLED is true
    # (dev/testing); production disables mock auth entirely.
    _MOCK_ADMIN_PASSWORD_HASH = (
        "$2b$12$5yLWERchOfPdEQrZEiY93.F5NkYqLaVGaOu6D4umiWiBQW9rnx./a"
    )

    def _ensure_initialized(self):
        """Ensure auth_handler is initialized, raise if not"""
        if not auth_handler.secret:
            raise RuntimeError("Auth handler not initialized - JWT secret is missing")

    def _mock_auth_enabled(self) -> bool:
        """Whether the temporary mock user store is allowed to accept logins."""
        try:
            from app import Application
            setting = Application.setting
        except Exception:
            setting = None
        # Default True so unit tests (which never build the app) keep working.
        return bool(getattr(setting, "MOCK_AUTH_ENABLED", True))

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """User login"""
        try:
            self._ensure_initialized()

            if not self._mock_auth_enabled():
                raise RuntimeError(
                    "Authentication is not configured - no user store available"
                )

            # TEMP: mock user store. Replace with a real database lookup.
            if username == "admin" and password_tools.verify_password(
                password, self._MOCK_ADMIN_PASSWORD_HASH
            ):
                # Generate JWT token
                token = auth_handler.generate_token(username)
                return {
                    "access_token": token,
                    "token_type": "bearer",
                    "expires_in": TOKEN_EXPIRES_IN,
                }
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
                    "sub": payload.get("sub"),
                    "exp": payload.get("exp"),
                    "iat": payload.get("iat"),
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

            # Revoke the old token (no point blacklisting an already-expired one)
            exp = payload.get("exp")
            if exp:
                remaining = exp - int(datetime.now(timezone.utc).timestamp())
                if remaining > 0:
                    auth_handler.revoke_token(token, exp_seconds=remaining)
            else:
                auth_handler.revoke_token(token)

            # Generate new token
            new_token = auth_handler.generate_token(payload.get("sub"))
            return {
                "access_token": new_token,
                "token_type": "bearer",
                "expires_in": TOKEN_EXPIRES_IN,
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
                    remaining = exp - int(datetime.now(timezone.utc).timestamp())
                    if remaining > 0:
                        auth_handler.revoke_token(token, exp_seconds=remaining)
                else:
                    auth_handler.revoke_token(token)
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise


# Create a global authentication service instance
auth_service = AuthService()

#!/usr/bin/env python
# encoding: utf-8
import jwt

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.requests import Request
from utils.logger import logger

ALGORITHM = "HS256"


class AuthHandler(object):
    def __init__(self, secret: str = None):
        self.security = HTTPBearer()
        self.secret = secret

    def initialize(self, secret: str):
        """Initialize the auth handler with a secret"""
        self.secret = secret

    def encode_token(self, payload: dict) -> str:
        """Encode a JWT token"""
        try:
            if not self.secret:
                raise ValueError("Secret not initialized")
            return jwt.encode(payload, self.secret, algorithm=ALGORITHM)
        except Exception as e:
            logger.error(f"Error encoding token: {e}")
            raise

    def generate_token(self, identity: str, expiration_sec: int = 86400 * 7) -> str:
        """Generate a JWT token for a user"""
        try:
            payload = {
                'exp': datetime.now(timezone.utc) + timedelta(seconds=expiration_sec),
                'iat': datetime.now(timezone.utc),
                'sub': identity,
            }
            token = self.encode_token(payload)
            return token
        except Exception as e:
            logger.error(f"Error generating token: {e}")
            raise

    def decode_token(self, token: str) -> Optional[dict]:
        """Decode and verify a JWT token"""
        try:
            if not self.secret:
                raise ValueError("Secret not initialized")
            payload = jwt.decode(token, self.secret, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error(f"Error decoding token: {e}")
            return None

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify a JWT token, checking blacklist if Redis is available"""
        payload = self.decode_token(token)
        if payload is None:
            return None

        # Check token blacklist via Redis
        if self._is_token_blacklisted(token):
            logger.warning("Token has been revoked")
            return None

        return payload

    def _is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is in the blacklist"""
        try:
            from app import Application
            redis_client = Application.redis_client
            if redis_client:
                return redis_client.get(f"token_blacklist:{token}") is not None
        except Exception:
            pass
        return False

    def revoke_token(self, token: str, exp_seconds: int = None):
        """Add a token to the blacklist. exp_seconds should match token's remaining TTL."""
        try:
            from app import Application
            redis_client = Application.redis_client
            if redis_client:
                # Default to 7 days if we can't determine remaining TTL.
                # Use "is not None" so an explicit 0 (token already expired)
                # does not accidentally fall back to the 7-day default.
                ttl = exp_seconds if exp_seconds is not None else 604800
                redis_client.set(f"token_blacklist:{token}", "1", expire=ttl)
        except Exception as e:
            logger.error(f"Error revoking token: {e}")

    def auth_wrapper(self, _: Request, oauth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> dict:
        """Auth wrapper for FastAPI dependencies"""
        payload = self.verify_token(oauth.credentials)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return payload


# Create a global auth handler instance
auth_handler = AuthHandler()

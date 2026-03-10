#!/usr/bin/env python
# encoding: utf-8
import jwt

from datetime import datetime, timedelta
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

    # encode jwt token
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

    # decode jwt token
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
        """Verify a JWT token"""
        payload = self.decode_token(token)
        if payload is None:
            return None
        return payload

    def auth_wrapper(self, _: Request, oauth: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> dict:
        """Auth wrapper for FastAPI dependencies"""
        payload = self.verify_token(oauth.credentials)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return payload


# Create a global auth handler instance
auth_handler = AuthHandler()

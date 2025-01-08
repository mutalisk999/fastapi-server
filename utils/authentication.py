#!/usr/bin/env python
# encoding: utf-8


import jwt

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.requests import Request

ALGORITHM = "HS256"


class AuthHandler(object):
    security = HTTPBearer()
    secret = None

    @staticmethod
    def initialize(secret: str):
        AuthHandler.secret = secret

    # encode jwt token
    @staticmethod
    def encode_token(payload: dict):
        return jwt.encode(payload, AuthHandler.secret, algorithm=ALGORITHM)

    @staticmethod
    def generate_token(identity: str, expiration_sec: int = 86400 * 7):
        payload = {
            'exp': datetime.utcnow() + timedelta(seconds=expiration_sec),
            'iat': datetime.utcnow(),
            'sub': identity,
        }
        token = AuthHandler.encode_token(payload)
        return token

    # decode jwt token
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, AuthHandler.secret, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        payload = AuthHandler.decode_token(token)
        if payload is None:
            return None
        return payload

    @staticmethod
    def auth_wrapper(_: Request, oauth: HTTPAuthorizationCredentials = Security(security)) -> Optional[dict]:
        return AuthHandler.verify_token(oauth.credentials)

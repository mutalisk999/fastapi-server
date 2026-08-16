#!/usr/bin/env python
# encoding: utf-8
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Lightweight email format check (avoids the extra email-validator dependency).
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_email(value: str) -> str:
    if not _EMAIL_RE.match(value):
        raise ValueError("Invalid email address")
    return value


class LoginRequest(BaseModel):
    """Login request model"""
    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    token: str = Field(..., min_length=1, description="Token to refresh")


class CreateUserRequest(BaseModel):
    """Create user request model"""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    email: str = Field(..., min_length=1, max_length=100, description="Email address")

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: str) -> str:
        return _validate_email(v)


class UpdateUserRequest(BaseModel):
    """Update user request model. All fields are optional; the caller must send
    at least one field, otherwise the update is a no-op (rejected by the route)."""
    username: Optional[str] = Field(None, max_length=50, description="Username")
    email: Optional[str] = Field(None, max_length=100, description="Email address")

    @field_validator("email")
    @classmethod
    def _check_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _validate_email(v)

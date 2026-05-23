#!/usr/bin/env python
# encoding: utf-8
from pydantic import BaseModel, Field


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


class UpdateUserRequest(BaseModel):
    """Update user request model"""
    username: str = Field(None, max_length=50, description="Username")
    email: str = Field(None, max_length=100, description="Email address")

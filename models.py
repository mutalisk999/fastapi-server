#!/usr/bin/env python
# encoding: utf-8
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class RefreshTokenRequest(BaseModel):
    token: str = Field(..., min_length=1)


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    email: str = Field(..., min_length=1, max_length=128)


class UpdateUserRequest(BaseModel):
    username: str | None = Field(None, min_length=1, max_length=64)
    email: str | None = Field(None, min_length=1, max_length=128)

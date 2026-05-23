#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter, HTTPException
from services.auth_service import auth_service
from utils.schemas import LoginRequest, RefreshTokenRequest

auth_router = APIRouter()


@auth_router.post("/login")
def login(login_data: LoginRequest):
    """User login"""
    try:
        token_info = auth_service.login(login_data.username, login_data.password)
        return token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/refresh")
def refresh_token(token_data: RefreshTokenRequest):
    """Refresh token"""
    try:
        new_token_info = auth_service.refresh_token(token_data.token)
        return new_token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
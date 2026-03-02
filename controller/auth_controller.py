#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from services.auth_service import auth_service

auth_router = APIRouter()


@auth_router.post("/login")
def login(login_data: Dict[str, Any]):
    """用户登录"""
    try:
        username = login_data.get("username")
        password = login_data.get("password")
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        token_info = auth_service.login(username, password)
        return token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@auth_router.post("/refresh")
def refresh_token(token_data: Dict[str, Any]):
    """刷新token"""
    try:
        token = token_data.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")
        
        new_token_info = auth_service.refresh_token(token)
        return new_token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
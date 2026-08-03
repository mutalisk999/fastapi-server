#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service
from utils.rate_limit import rate_limit
from models import LoginRequest, RefreshTokenRequest

auth_router = APIRouter()
security = HTTPBearer()


@auth_router.post("/login")
@rate_limit(max_requests=5, window_seconds=60)
async def login(request: Request, login_data: LoginRequest):
    """用户登录"""
    try:
        token_info = auth_service.login(login_data.username, login_data.password)
        return token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Service configuration error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/refresh")
async def refresh_token(token_data: RefreshTokenRequest):
    """刷新token"""
    try:
        new_token_info = auth_service.refresh_token(token_data.token)
        return new_token_info
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError:
        raise HTTPException(status_code=500, detail="Service configuration error")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@auth_router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出，撤销token"""
    try:
        token = credentials.credentials
        auth_service.logout(token)
        return {"message": "Successfully logged out"}
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

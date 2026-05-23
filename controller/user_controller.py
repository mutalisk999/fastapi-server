#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.user_service import user_service
from services.auth_service import auth_service
from utils.schemas import CreateUserRequest, UpdateUserRequest

user_router = APIRouter()
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current user"""
    token = credentials.credentials
    user_info = auth_service.verify_token(token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_info


@user_router.get("/users/{user_id}")
def get_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user information"""
    try:
        user_info = user_service.get_user_info(user_id)
        return user_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.post("/users")
def create_user(user_data: CreateUserRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Create user"""
    try:
        new_user = user_service.create_user(user_data.model_dump())
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.put("/users/{user_id}")
def update_user(user_id: str, user_data: UpdateUserRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Update user information"""
    try:
        updated_user = user_service.update_user(user_id, user_data.model_dump(exclude_none=True))
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@user_router.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    """Delete user"""
    try:
        result = user_service.delete_user(user_id)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
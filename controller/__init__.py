#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter

mock_router = APIRouter()
from controller.user_controller import user_router
from controller.auth_controller import auth_router


@mock_router.get("/hello")
def hello():
    return dict(slogan="Hello World!")

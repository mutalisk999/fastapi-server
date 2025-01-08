#!/usr/bin/env python
# encoding: utf-8
from fastapi import APIRouter

mock_router = APIRouter()


@mock_router.get("/hello")
def hello():
    return dict(slogan="Hello World!")

#!/usr/bin/env python
# encoding: utf-8

from decimal import Decimal


def decimal_serializer(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Type not serializable")

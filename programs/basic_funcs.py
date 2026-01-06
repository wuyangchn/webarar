#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - basic_funcs.py
# ==========================================
#
#
# 
"""

import pickle
import string
import random
from django.core.cache import cache


DEFAULT_CACHE_TIMEOUT = 86400
ALPHABET = string.ascii_lowercase + string.digits


def random_choice(length: int = 8) -> str:
    return ''.join(random.choices(ALPHABET, k=length))


def set_cache(obj, key='', user_id=''):
    """
    Create (leave key default) or update cache (give key). This is used to link sample
    instance with cache key, which is an unique identifier for this object in the cache.
    The cache key will also be sent to user so that changes from front can be identified.
    """
    if not key:
        key = random_choice(length=8)
    _cache_key = f"user:{user_id}:data:{key}:obj" if user_id else key
    value = pickle.dumps(obj)
    cache.set(_cache_key, value, timeout=DEFAULT_CACHE_TIMEOUT)
    return key


def get_cache(key, default=None):
    """
    Get cache
    """
    return pickle.loads(cache.get(key, default=default))


def touch_cache(key):
    """
    Update last accessed time/last used time

    """
    return cache.touch(key, timeout=DEFAULT_CACHE_TIMEOUT, version=None)


def set_sql(mysql, user_id, **kwargs):
    if mysql.objects.filter(uuid=str(user_id)).exists():
        _user = mysql.objects.get(uuid=str(user_id))
        for key, val in kwargs.pop('uuid').items():
            setattr(_user, key, val)
        _user.save()
    else:
        mysql.objects.create(**kwargs)


def get_ip(request):
    """
    Get ipv4 address from requests
    """
    if request.META.get('HTTP_X_FORWARDED_FOR'):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_device(request):
    """
    Get device information of user browser
    """
    # print('请求相关的信息：', request.environ)  # environ里面有请求的所有信息
    # print('设备信息：', request.environ.get("HTTP_USER_AGENT"))  # 全部返回的是个字典
    try:
        return request.environ.get("HTTP_USER_AGENT")
    except AttributeError:
        return "AttributeError"


def get_lang(request):
    """
    Get language setting of user browser
    """
    try:
        return request.environ.get("HTTP_ACCEPT_LANGUAGE")
    except AttributeError:
        return "This is ASGIRequest"


def is_ajax(request):
    """
    Return if the request is from ajax
    """
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"

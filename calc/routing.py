#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - routing.py
# ==========================================
#
#
# 
"""

from django.urls import re_path
from programs import ws_funcs

websocket_urlpatterns = [
    # 匹配 ws请求，捕获 task_id作为参数
    re_path(r'ws/progress/(?P<task_id>[^/]+)/$', ws_funcs.ProgressConsumer.as_asgi()),
]
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - consumers
# ==========================================
#
#
# 
"""
import threading
import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from . import models
from programs import basic_funcs, ws_funcs


def as_view(cls, request, *args, **kwargs):
    if "flag" in kwargs.keys():
        flag = kwargs['flag']
        handler = globals().get(flag)
    else:
        raise KeyError
    print("flag: %s" % handler.__name__)
    return handler(cls, request, *args, **kwargs)


# request method
@require_POST
def ws_raw_regression(cls, request, *args, **kwargs):

    try:
        files = json.loads(request.body)['files']
    except json.decoder.JSONDecodeError:
        return JsonResponse({"code": 400, "error": "No file uploaded or file upload failed."})
    file_names = [each['file_name'] for each in files if each['checked']]
    file_paths = [each['file_path'] for each in files if each['checked']]
    file_paths = [os.path.join(settings.UPLOAD_ROOT, f"{each}") for each in file_paths]
    filter_names = [each['filter'] for each in files if each['checked']]
    filter_paths = [
        getattr(models, "InputFilterParams").objects.get(name=each).file_path for each in filter_names
    ]

    task_id = basic_funcs.random_choice(length=8)
    ready_event = threading.Event()
    ws_funcs.task_ready_events[task_id] = ready_event
    threading.Thread(target=ws_funcs.raw_regression,
                     args=(cls, task_id, file_names, file_paths, filter_names, filter_paths)).start()
    return JsonResponse({"code": 200, "task_id": task_id})


@require_POST
def ws_recalculation(cls, request, *args, **kwargs):
    task_id = basic_funcs.random_choice(length=8)
    ready_event = threading.Event()  # 建立事件用于检测连接是否就绪
    ws_funcs.task_ready_events[task_id] = ready_event
    # 启动子线程
    threading.Thread(target=ws_funcs.recalculate, args=(cls, task_id, )).start()
    return JsonResponse({"code": 200, "task_id": task_id})


@require_POST
def ws_click_chart(cls, request, *args, **kwargs):
    task_id = basic_funcs.random_choice(length=8)
    ready_event = threading.Event()  # 建立事件用于检测连接是否就绪
    ws_funcs.task_ready_events[task_id] = ready_event
    # 启动子线程
    threading.Thread(target=ws_funcs.click_chart, args=(cls, task_id, )).start()
    return JsonResponse({"code": 200, "task_id": task_id})


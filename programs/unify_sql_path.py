#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2026 Yang 
# webarar - unify_sql_path
# ==========================================
#
#
# 
"""


from pathlib import Path, PurePosixPath, PureWindowsPath
from django.conf import settings


def is_absolute_path(value):
    value = str(value or "").strip()
    return (
        PureWindowsPath(value).is_absolute()
        or PurePosixPath(value).is_absolute()
    )


def get_setting_filename(value):
    value = str(value or "").strip()
    if not value:
        raise ValueError("Empty setting file path")

    filename = PureWindowsPath(value).name
    if not filename or filename in {".", ".."}:
        raise ValueError(f"Invalid setting file path: {value}")

    return filename


def get_setting_path(value):
    filename = get_setting_filename(value)
    return Path(settings.SETTINGS_ROOT) / filename

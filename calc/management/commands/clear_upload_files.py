#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2025 Yang 
# webarar - clear_upload_files
# ==========================================
#
#
# 
"""
import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from calc.models import ReceivedFiles


class Command(BaseCommand):

    help = 'Clear uploaded fold regularly (files uploaded > 24 hours ago are automatically cleared on 00:00 every day.)'

    def handle(self, *args, **options):
        file_ops = {
            "deleted": [],  # 成功物理删除的文件路径
            "failed": []  # 物理删除失败的文件（含原因）
        }
        # 1. 计算目标删除日期：今天 - 2天（如今天1月5日→目标1月3日）
        now = timezone.now()
        target_delete_date = now - timedelta(days=1)
        self.stdout.write(f'Start to delete files uploaded before「{target_delete_date}」')

        # 2. 筛选目标日期的文件（仅删当天00:00~23:59上传的文件）
        # 注意：模型需有「上传时间字段」（如 upload_time，DateTimeField 类型）
        expired_files = ReceivedFiles.objects.filter(
            # 筛选 upload_time 的「日期部分」等于 target_delete_date
            insert_time__lt=target_delete_date,
            deleted=False  # 仅删除未被手动删除的文件
        ).values_list('file_path', flat=True)

        expired_count = expired_files.count()
        if expired_count == 0:
            self.stdout.write(self.style.SUCCESS(f'No files uploaded before「{target_delete_date}」'))
            return

        for path in expired_files:
            try:
                os.remove(path)
                file_ops["deleted"].append(path)
            except Exception as e:
                file_ops["failed"].append({
                    "path": path,
                    "error": str(e),
                    "error_type": type(e).__name__
                })

        ReceivedFiles.objects.filter(file_path__in=file_ops['deleted']).update(deleted=True, deleted_time=timezone.now())

        msg = f"{expired_count} files expired, {len(file_ops['deleted'])} files deleted, "
        for each in file_ops['failed']:
            msg += f"path = {each['path']}, error = {each['error']} | "
        self.stdout.write(self.style.SUCCESS(msg))

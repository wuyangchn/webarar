"""
ASGI config for webarar project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import calc.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webarar.settings')

# 核心：先用 ASGIStaticFilesHandler 处理静态文件，再路由分发请求
application = ASGIStaticFilesHandler(
    ProtocolTypeRouter({
        # HTTP 同步请求：走 Django 原有逻辑
        "http": get_asgi_application(),
        # WebSocket/长连接请求：走自定义路由
        "websocket": AuthMiddlewareStack(
            URLRouter(
                calc.routing.websocket_urlpatterns
            )
        ),
    })
)

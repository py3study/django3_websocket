# ！/usr/bin/python3
# -*- coding: utf-8 -*-
# asgi.py
import os

from django.core.asgi import get_asgi_application

from web.websocket import websocket_application

# 注意修改应用名
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django3_websocket.settings')

django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope['type'] == 'http':
        await django_application(scope, receive, send)
    elif scope['type'] == 'websocket':
        await websocket_application(scope, receive, send)
    else:
        raise NotImplementedError(f"Unknown scope type {scope['type']}")

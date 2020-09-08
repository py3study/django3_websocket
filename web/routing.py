# ！/usr/bin/python3
# -*- coding: utf-8 -*-
from django.urls import re_path,path

from . import consumers

websocket_urlpatterns = [
    # 前端请求websocket连接
    path('ws/result/', consumers.SyncConsumer),
]
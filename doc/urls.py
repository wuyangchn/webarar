from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_view, name="doc_main_view"),
    path('en', views.doc_en, name="doc_en"),
    path('zh', views.doc_zh, name="doc_zh"),
    path('tutorial', views.tutorial, name="tutorial"),
    path('deploy', views.deploy, name="deploy"),
    path('update_log', views.update_log, name="update_log"),
]

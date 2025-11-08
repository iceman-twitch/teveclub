"""
URL configuration for bot_api app
Single proxy endpoint - forwards requests to teveclub.hu
"""
from django.urls import path
from . import views

urlpatterns = [
    path('proxy/', views.proxy, name='proxy'),
]

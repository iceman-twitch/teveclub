"""
URL configuration for bot_api app
"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('feed/', views.feed, name='feed'),
    path('learn/', views.learn, name='learn'),
    path('guess/', views.guess_game, name='guess'),
    path('logout/', views.logout, name='logout'),
]

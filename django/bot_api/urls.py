"""
URL configuration for bot_api app
Single proxy endpoint - forwards requests to teveclub.hu
"""
from django.urls import path
from . import views

urlpatterns = [
    path('proxy/', views.proxy, name='proxy'),
    path('get-current-food-drink/', views.get_current_food_drink, name='get_current_food_drink'),
    path('get-current-trick/', views.get_current_trick, name='get_current_trick'),
]

from django.urls import path
from . import views


urlpatterns = [
    path('', views.apiView, name='api'),
    path('rooms/', views.getRooms, name='get-rooms'),
    path('rooms-class/', views.getRooms, name='get-rooms-class'),
]
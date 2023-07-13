from django.urls import path
from django.conf.urls import include
from config import views

urlpatterns = [
    path('', views.ConfigRequest, name='config-request'),
    path('watering/', views.WateringRequest, name='watering-request'),
]

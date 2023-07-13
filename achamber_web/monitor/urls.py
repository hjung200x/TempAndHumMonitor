from django.urls import path
from django.conf.urls import include
from monitor import views

urlpatterns = [
    path('', views.MonitorGraph, name='monitor-graph'),
    path('delete_all/', views.DeleteAllMonitorData, name='delete-all'),
]

from django.urls import path
from . import views

urlpatterns = [
    
    path('add_tv/', views.add_tv, name='add_tv'),  
    path('delete_tv/<int:tv_id>/', views.delete_tv, name='delete_tv'),
    path('start-check/', views.start_check, name='start_check'),
    path('', views.tv_status_view, name='tv_status'), 
    path('tv-report/', views.tv_report_view, name='tv_report'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_reports, name='admin_reports'),
]
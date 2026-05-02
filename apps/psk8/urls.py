from django.urls import path
from . import views

app_name = 'psk8'

urlpatterns = [
    path('', views.home, name='home'),
]
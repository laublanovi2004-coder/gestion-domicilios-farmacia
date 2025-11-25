from django.urls import path
from . import views

app_name = 'domicilios'

urlpatterns = [
    path('', views.index, name='index'),
]
from django.urls import path

from . import views


app_name = 'convert'
urlpatterns = [
    path('', views.index, name='index'),
]

from django.urls import path

from . import views
from .views import CurrencyRateListView

app_name = 'convert'
urlpatterns = [
    path('', views.index, name='index'),  # <-- updated URL path for home page
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('<str:currency_from>-<str:currency_to>/', CurrencyRateListView.as_view(), name='currency_rates'),
]

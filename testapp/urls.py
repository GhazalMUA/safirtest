from django import urls
from django.urls import path
from .views import create_order

app_name='testapp'
urlpatterns = [
    path('ordercreation/', create_order, name='order_creation')
    ]

from django.urls import path
from . import views

urlpatterns = [
    path('customers/', views.customers, name='customers'),
    path('customer-create/', views.customer_create, name='customer_create')
]

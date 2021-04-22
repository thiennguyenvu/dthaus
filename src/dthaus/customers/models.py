from django.db import models
from django.contrib import auth
from django.utils.timezone import now
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    CUSTOMER_TYPES = (
        ('Loyal Customers', 'Loyal Customers'),
        ('Impulse Shoppers', 'Impulse Shoppers'),
        ('Bargain Hunters', 'Bargain Hunters'),
        ('Wandering Consumers', 'Wandering Consumers'),
        ('Need-Based Customers', 'Need-Based Customers'),
    )
    customer_type = models.CharField(max_length=25, default='Loyal Customers',
                                     choices=CUSTOMER_TYPES, help_text='Consumer-based marketing')
    date_created = models.DateTimeField(auto_now_add=True)
    address = models.TextField(null=True)
    phone_number = PhoneNumberField(null=False, unique=True)
    email = models.EmailField(max_length=254, null=True)

    def __str__(self):
        return self.name
from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser

class UserManagement(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=f"avatar")
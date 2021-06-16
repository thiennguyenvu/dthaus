from django.db import models
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class DJPermission(models.Model):
    name = models.CharField(max_length=20)
    codename = models.CharField(max_length=20, blank=True)

    def save(self, *args, **kwargs):  # Auto create codename depend name
        if not self.codename:
            self.codename = str(self.name).lower()
        super(DJPermission, self).save(*args, **kwargs)

    def __str__(self):
        return self.codename


class UserGroup(models.Model):
    OBJECT_TYPE = (
        ('project', 'project'),
        ('phase', 'phase'),
        ('task', 'task'),
    )
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE)
    object_id = models.PositiveIntegerField()
    permission = models.ManyToManyField(DJPermission)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{str(self.object_type)}_{str(self.object_id)}_per"
        super(UserGroup, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserManagement(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.CharField(max_length=10, null=True, blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=f"avatar")
    user_group = models.ManyToManyField(UserGroup, blank=True)


class UserLogFile(models.Model):
    action_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action_code = models.CharField(max_length=20)
    object_type = models.CharField(max_length=50)
    object_id = models.IntegerField()
    change_message = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user}_{self.action_code}_{self.object_type}_id_{self.object_id}"

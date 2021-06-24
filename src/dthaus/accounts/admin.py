from django.contrib import admin
# Register your models here.
from .models import *

admin.site.register(UserManagement)
admin.site.register(UserGroup)
admin.site.register(UserLogFile)
admin.site.register(DJPermission)
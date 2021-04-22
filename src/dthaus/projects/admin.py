from django.contrib import admin
# Register your models here.
from .models import Project, Phase, CustomPhase, Task, CustomTask
admin.site.register(Project)
admin.site.register(Phase)
admin.site.register(CustomPhase)
admin.site.register(Task)
admin.site.register(CustomTask)
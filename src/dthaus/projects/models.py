from django.db import models
from django.contrib import auth
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from django.core.files.storage import default_storage
# Create your models here.
from customers.models import Customer
from accounts.models import UserManagement


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300, unique=True)
    description = models.TextField(blank=True, null=True)
    STATUS = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('QA Review', 'QA Review'),
        ('Incomplete', 'Incomplete'),
        ('Client Review', 'Client Review'),
        ('Approved/Paid', 'Approved/Paid'),
        ('Finished', 'Finished'),
        ('On Hold', 'On Hold'),
        ('Repossessed', 'Repossessed'),
    )
    status = models.CharField(max_length=25, default='In Progress',
                              choices=STATUS, help_text='default status: In Progress')
    PRIORITY = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent'),
    )
    priority = models.CharField(max_length=10, default='Medium',
                                choices=PRIORITY, help_text='default priority: Medium')
    date_created = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(default=now)
    due_date = models.DateTimeField(null=True)
    progress = models.IntegerField(default=0)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    phase_order = models.BooleanField(default=True)
    date_finished = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Phase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    phase_name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField(default=now)
    due_date = models.DateTimeField(default=now)
    STATUS = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
        ('Complete Overdue', 'Complete Overdue'),
    )
    phase_status = models.CharField(
        max_length=25, choices=STATUS, default='In Progress')
    phase_finished = models.BooleanField(default=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.phase_name


class CustomPhase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    selected = models.BooleanField(default=True)
    phase_name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.phase_name


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    date_created = models.DateTimeField(auto_now_add=True)
    task_name = models.CharField(max_length=300)
    description = models.TextField(blank=True, null=True)
    start_date_upload = models.DateTimeField(default=now)
    due_date_upload = models.DateTimeField(default=now)
    user_upload = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='user_upload')
    start_date_approve = models.DateTimeField(default=now)
    due_date_approve = models.DateTimeField(default=now)
    user_approve = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, related_name='user_approve')
    STATUS = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
        ('Completed Overdue', 'Completed Overdue'),
    )
    task_status = models.CharField(
        max_length=25, choices=STATUS, default='In Progress')
    upload_status = models.CharField(max_length=25, choices=STATUS, default='In Progress')
    approve_status = models.CharField(max_length=25, choices=STATUS, default='In Progress')
    task_finished = models.BooleanField(default=False)
    date_finished = models.DateTimeField(null=True)
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.task_name


class CustomTask(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    selected = models.BooleanField(default=True)
    task_name = models.CharField(max_length=300, unique=True)

    def __str__(self):
        return self.task_name


class TaskFiles(models.Model):
    date_uploaded = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    url = models.CharField(max_length=300, null=True, blank=True)
    attachment = models.FileField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(UserManagement, on_delete=models.CASCADE, null=True, blank=True)
    file_approved = models.BooleanField(default=False)
    file_rejected = models.BooleanField(default=False)
    note = models.CharField(max_length=300, null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.projects, name='projects'),
    path('projects/create-project/', views.project_create, name='project_create'),
    path('projects/update-project-<str:pk_project>/',
         views.project_update, name='project_update'),
    path('projects/delete-project-<str:pk_project>/',
         views.project_delete, name='project_delete'),

    # Project Phase
    path('project-<str:pk_project>/phase-settings/',
         views.phase_settings, name='phase_settings'),
    path('project-<str:pk_project>/phase-edit/',
         views.phase_edit, name='phase_edit'),

    # Project Task
    path('project-<str:pk_project>/phase-<str:pk_phase>/task-settings/',
         views.task_settings, name='task_settings'),
    path('project-<str:pk_project>/phase-<str:pk_phase>/task-views/',
         views.task_views, name='task_views'),
    path('project-<str:pk_project>/phase-<str:pk_phase>/task-<str:pk_task>/',
         views.task_edits, name='task_edits'),
    path('project-<str:pk_project>/phase-<str:pk_phase>/task-<str:pk_task>/delete/',
         views.task_delete, name='task_delete')
]

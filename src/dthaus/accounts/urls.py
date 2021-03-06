from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutPage, name='logout'),
    path('profiles/<str:username>', views.profiles, name='profiles'),
    path('settings/<str:username>', views.settings, name='settings'),
    path('register/', views.register, name='register'),
    path('user-management/', views.user_management, name='user_management'),
    path('group-settings/', views.group_settings, name='group_settings'),
    path('group-permissions/<str:object_type>-<str:object_id>', views.group_permissions, name='group_permissions'),
    path('group-management/group-<str:id_group>', views.group_management, name='group_management'),
    path('customers/', views.customers, name='customers'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

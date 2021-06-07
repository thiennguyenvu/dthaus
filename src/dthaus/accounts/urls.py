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
    path('group-create/', views.group_create, name='group_create'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

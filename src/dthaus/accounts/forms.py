from django import forms
from django.forms import ModelForm, modelformset_factory
from .models import *

class DateInput(forms.DateInput):
    input_type = 'date'


class UserProfileForm(ModelForm):
    class Meta:
        model = UserManagement
        fields = ['first_name', 'last_name', 'email',
                  'birth_date', ]
        widgets = {
            'birth_date': DateInput(),
            'date_joined': forms.TextInput(),
            'last_login': forms.TextInput(),
        }


class UserPasswordForm(ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserManagement
        fields = ('password', 'confirm_password', )
        widgets = {
            'password': forms.PasswordInput(),
        }


class UserBioForm(ModelForm):
    class Meta:
        model = UserManagement
        fields = ('bio',)


class UserAvatarForm(ModelForm):
    class Meta:
        model = UserManagement
        fields = ('avatar',)


class UserRegisterForm(ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserManagement
        fields = '__all__'
        exclude = ('is_superuser', 'last_login',
                   'is_staff', 'user_permissions', 'date_joined', 'is_active')
        widgets = {
            'birth_date': DateInput(),
            'password': forms.PasswordInput(),
        }

class UserManagementForm(ModelForm):
    class Meta:
        model = UserManagement
        fields = '__all__'
        widgets = {
            'birth_date': DateInput(),
        }

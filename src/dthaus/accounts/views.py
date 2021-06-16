from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash
from datetime import datetime
from django.utils import timezone
from django.conf import settings as dthaus_settings

from .models import *
from .forms import GroupSettingsForm, ObjectTypeForm, UserBioForm, UserAvatarForm, UserPasswordForm, \
    UserProfileForm, UserRegisterForm, UserManagementForm

# Create your views here.
brand = 'DONGJIN VIETNAM J.S.C'


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:  # Login with email as username
                user_email = ''
                try:
                    user_email = UserManagement.objects.get(email=username)
                    user = authenticate(
                        request, username=user_email, password=password)
                    if user is not None:
                        login(request, user)
                        return redirect('home')
                    else:
                        messages.add_message(
                            request, messages.ERROR, 'Username or Password is incorrect')
                except:
                    messages.add_message(
                        request, messages.ERROR, 'Username or Password is incorrect')

        return render(request, 'accounts/login.html')


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home(request):
    title = 'Dashboard'
    context = {
        'brand': brand,
        'title': title,
    }
    return render(request, 'accounts/dashboard.html', context=context)


@login_required(login_url='login')
def profiles(request, username):
    title = 'Profiles'
    user = request.user
    bio_form = UserBioForm()
    avatar_form = UserAvatarForm()

    if request.method == 'POST':
        if 'btn-change-bio' in request.POST:
            form = UserBioForm(request.POST, instance=user)
            if form.is_valid():
                form.save()

        if 'btn-change-avatar' in request.POST:
            form = UserAvatarForm(request.POST, request.FILES, instance=user)
            print(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('profiles', username=user.username)

    context = {
        'brand': brand,
        'title': title,
        'bio_form': bio_form,
        'avatar_form': avatar_form,
    }
    return render(request, 'accounts/profiles.html', context=context)


@login_required(login_url='login')
def settings(request, username):
    title = 'Settings & Privacy'
    user = request.user
    password_form = UserPasswordForm()
    profile_form = UserProfileForm()

    if request.method == 'POST':
        if 'save-password' in request.POST:
            form = UserPasswordForm(request.POST, instance=user)
            if form.is_valid():
                setting = form.save(commit=False)
                current_password = form.cleaned_data['current_password']
                # Check user current password
                if check_password(current_password, user.password):
                    new_password = form.cleaned_data['new_password']
                    confirm_password = form.cleaned_data['confirm_password']
                    if new_password == confirm_password:
                        # Hash password
                        setting.password = make_password(new_password)
                        setting.save()
                        # Keep session when user change password
                        update_session_auth_hash(request, user)
                        messages.add_message(
                            request, messages.SUCCESS, 'Password update successfully.')

                    else:
                        messages.add_message(
                            request, messages.ERROR, "Password confirmation doesn't match password.")
                else:
                    messages.add_message(
                        request, messages.ERROR, 'Invalid password.')

        if 'save-profile' in request.POST:
            form = UserProfileForm(request.POST, instance=user)

            if form.is_valid():
                form.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Profile updated.')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Form is invalid.')

    context = {
        'brand': brand,
        'title': title,
        'password_form': password_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/settings.html', context=context)


@login_required(login_url='login')
def register(request):
    title = 'Register Page'

    register_form = UserRegisterForm()

    if request.method == 'POST':
        form = UserRegisterForm(request.POST or None, request.FILES)
        if form.is_valid():
            setting = form.save(commit=False)
            plain_password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            if plain_password == confirm_password:
                setting.password = make_password(plain_password)
                setting.save()

                messages.add_message(request, messages.SUCCESS,
                                     'Create user successfully.')
                return redirect('user_management')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Password does not match.')
        else:
            messages.add_message(request, messages.ERROR, form.errors)

    context = {
        'brand': brand,
        'title': title,
        'register_form': register_form,
    }
    return render(request, 'accounts/register.html', context=context)


@login_required(login_url='login')
def user_management(request):
    title = 'User Management'
    user_list = UserManagement.objects.all()

    context = {
        'brand': brand,
        'title': title,
        'user_list': user_list,
    }
    return render(request, 'accounts/user-management.html', context=context)


@login_required(login_url='login')
def group_settings(request):
    title = 'Group Settings'
    groups = ''

    obj_type_form = ObjectTypeForm()
    object_type = ''

    if request.method == 'GET':
        obj_type_form = ObjectTypeForm(request.GET or None)
        if obj_type_form.is_valid():
            object_type = request.GET['object_type']
            print(object_type)
            groups = UserGroup.objects.filter(object_type=object_type)

    context = {
        'brand': brand,
        'title': title,
        'groups': groups,
        'obj_type_form': obj_type_form,
    }
    return render(request, 'accounts/group-settings.html', context=context)


@login_required(login_url='login')
def group_create(request):
    title = 'Group Create'
    group_form = GroupSettingsForm()

    if request.method == 'POST':
        group_form = GroupSettingsForm(request.POST or None)
        if group_form.is_valid():
            group_form.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Create group successfully.')
            return redirect(group_settings)
        else:
            messages.add_message(request, messages.ERROR, 'Invalid form')

    context = {
        'brand': brand,
        'title': title,
        'group_form': group_form,
    }
    return render(request, 'accounts/group-create.html', context=context)


# def send_email(request, subject, msg_str, recepients):
#     title = 'Send Email'
#     subject = 'Welcome to DTHaus!'
#     msg_str = 'This is an automated email of DTHaus - Thien Nguyen Vu'
#     recepients = ['tnv.phoenix@gmail.com']
#     send_mail(subject, msg_str, dthaus_settings.EMAIL_HOST_USER,
#               recepients, fail_silently=False)

#     context = {
#         'brand': brand,
#         'title': title,
#     }
#     return render(request, 'accounts/send-email.html', context=context)

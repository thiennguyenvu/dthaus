from django.contrib.auth.models import Group, User
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
from django.db.models import Q

from .models import *
from .forms import GroupSettingsForm, ObjectTypeForm, SelectedUserForm, UserBioForm, UserAvatarForm, UserPasswordForm, \
    UserProfileForm, UserRegisterForm, UserManagementForm, UserSelectForm
from projects.models import *
from projects.forms import *
from projects.views import all_permission

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
    title = 'User Register'

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
def customers(request):
    title = 'Customers'
    customers = UserManagement.objects.filter(is_customer=True)
    
    context = {
        'brand': brand,
        'title': title,
        'customers': customers,
    }
    return render(request, 'accounts/customers.html', context=context)


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

    projects = []
    phases = []
    tasks = []
    project_per_add = False
    project_per_change = False
    project_per_delete = False

    if request.user.is_superuser:
        projects = Project.objects.all()
        phases = Phase.objects.all()
        tasks = Task.objects.all()
        project_per_add = True
        project_per_change = True
        project_per_delete = True
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'view':
                # Permission view project
                if permission['object_type'] == 'project':
                    _project = Project.objects.get(id=permission['object_id'])
                    if _project not in projects:
                        projects.append(_project)

                        for _phase in Phase.objects.filter(project=_project):
                            if _phase not in phases:
                                phases.append(_phase)
                            for _task in Task.objects.filter(phase=_phase):
                                if _task not in tasks:
                                    tasks.append(_task)

                # Permission view phase
                if permission['object_type'] == 'phase':
                    _phase = Phase.objects.get(id=permission['object_id'])
                    if _phase not in phases:
                        phases.append(_phase)
                        _project = _phase.project

                        if _project not in projects:
                            projects.append(_project)

                        for _task in Task.objects.filter(phase=_phase):
                            if _task not in tasks:
                                tasks.append(_task)

                # Permission view task
                if permission['object_type'] == 'task':
                    task = Task.objects.get(id=permission['object_id'])
                    if task not in tasks:
                        tasks.append(task)
                        phase = task.phase
                        project = phase.project

                        if phase not in phases:
                            phases.append(phase)
                        if project not in projects:
                            projects.append(project)

            # Permission
            if permission['object_type'] == 'project':
                if str(permission['permission']) == 'add':
                    project_per_add = True
                if str(permission['permission']) == 'change':
                    project_per_change = True
                if str(permission['permission']) == 'delete':
                    project_per_delete = True

    form_select = ProjectSelectedForm()  # Select id of project
    choice_project = ''
    if request.method == 'POST':
        form_select = ProjectSelectedForm(request.POST)
        if form_select.is_valid():
            form_select.id_selected = request.POST['id_selected']
            choice_project = Project.objects.get(id=form_select.id_selected)

    context = {
        'brand': brand,
        'title': title,
        'projects': projects,
        'phases': phases,
        'tasks': tasks,
        'project_per_add': project_per_add,
        'project_per_change': project_per_change,
        'project_per_delete': project_per_delete,
        'form_select': form_select,
        'choice_project': choice_project,
        'groups': groups,
        'obj_type_form': obj_type_form,
    }
    return render(request, 'accounts/group-settings.html', context=context)


@login_required(login_url='login')
def group_permissions(request, object_type, object_id):
    title = 'Group Permissions'
    groups = UserGroup.objects.filter(
        object_type=object_type, object_id=object_id)

    object_name = ''
    if object_type == 'project':
        object_name = Project.objects.get(id=object_id).name
    if object_type == 'phase':
        object_name = Phase.objects.get(id=object_id).name
    if object_type == 'task':
        object_name = Task.objects.get(id=object_id).name

    group_form = GroupSettingsForm()
    if request.method == 'POST':
        group_form = GroupSettingsForm(request.POST or None)
        if group_form.is_valid():
            auto = group_form.save(commit=False)
            auto.object_type = object_type
            auto.object_id = object_id
            per = ''
            if '1' in request.POST.getlist('permission'):
                per += '_add'
            if '2' in request.POST.getlist('permission'):
                per += '_change'
            if '3' in request.POST.getlist('permission'):
                per += '_delete'
            auto.name = f"{object_type}_{object_id}_view{per}"

            # Check exist
            name_exist = ''
            try:
                name_exist = UserGroup.objects.get(
                    object_type=object_type, object_id=object_id, name=auto.name)
            except:
                name_exist = ''
            if not name_exist:
                auto.save()
                group_form.save_m2m()
                messages.add_message(request, messages.SUCCESS,
                                     f"<b>{auto.name}</b> was added successfully.", extra_tags='safe')
            else:
                messages.add_message(
                    request, messages.WARNING, f"<b>{auto.name}</b> is already exist in Groups", extra_tags='safe')
            print(request.POST)

    context = {
        'brand': brand,
        'title': title,
        'group_form': group_form,
        'object_name': object_name,
        'object_id': object_id,
        'object_type': object_type,
        'groups': groups,
    }
    return render(request, 'accounts/group-permissions.html', context=context)


@login_required(login_url='login')
def group_management(request, id_group):
    title = 'Group Management'
    group = UserGroup.objects.get(id=id_group)
    user_group = UserManagement.objects.filter(user_group=group)
    form = UserSelectForm()
    selected_form = SelectedUserForm()
    users = ''
    if request.method == 'POST':
        if 'btn-find-user' in request.POST:
            form = UserSelectForm(request.POST)
            if form.is_valid():
                keyword = request.POST['find_user']
                users = UserManagement.objects.filter(
                    Q(username__startswith=keyword) | Q(email__startswith=keyword))[:10]

        if 'btn-select-user-add' in request.POST:
            selected_form = SelectedUserForm(request.POST)
            if selected_form.is_valid():
                selected_user = request.POST['selected_user']
                user = UserManagement.objects.get(username=selected_user)
                if not user.is_superuser:
                    try:
                        exist = UserManagement.objects.get(username=selected_user, user_group=group)
                    except:
                        exist = None
                    if not exist:
                        user.user_group.add(group)
                        subject = f"{dthaus_settings.EMAIL_HOST_USER} invited you to group {group.name}"
                        msg_str = f"{request.user} added you to group."
                        recepients = [user.email]
                        messages.add_message(
                            request, messages.SUCCESS, 'User was added successfully. Email was sent to user.')
                        send_mail(subject, msg_str, dthaus_settings.EMAIL_HOST_USER,
                                recepients, fail_silently=False)
                    else:
                        messages.add_message(request, messages.ERROR, f"User <b>{user}</b> already in this group", extra_tags='safe')

        if 'btn-select-user-delete' in request.POST:
            selected_form = SelectedUserForm(request.POST)
            if selected_form.is_valid():
                selected_user = request.POST['selected_user']
                user = UserManagement.objects.get(username=selected_user)
                if not user.is_superuser:
                    user.user_group.remove(group)

    context = {
        'brand': brand,
        'title': title,
        'group': group,
        'user_group': user_group,
        'form': form,
        'selected_form': selected_form,
        'users': users,
    }
    return render(request, 'accounts/group-management.html', context=context)

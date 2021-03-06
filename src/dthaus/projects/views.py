from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.forms import inlineformset_factory, modelformset_factory
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from django.shortcuts import get_object_or_404

from accounts.models import DJPermission
from accounts.models import UserGroup
from accounts.models import UserLogFile

# Create your views here.
from .models import *
from .forms import ProjectCreateForm, PhaseCreateForm, ListPhaseForm, \
    TaskCreateForm, ListTaskForm, FileCreateForm, FileApproveForm, ProjectSelectedForm

brand = 'DONGJIN VIETNAM J.S.C'


def all_permission(request):
    permission = []

    if request.user.user_group.all():
        for group in request.user.user_group.all():
            per_group = group.permission.all()
            for per in per_group:
                data = {}
                data['object_type'] = group.object_type
                data['object_id'] = group.object_id
                data['permission'] = per

                if data not in permission:
                    permission.append(data)

    return permission


def has_permission(request, object_type, object_id, permission):
    if request.user.user_group.all():
        for group in request.user.user_group.all():
            per_group = group.permission.all()
            for per in per_group:
                if group.object_type == object_type and str(group.object_id) == str(object_id) and per.codename == permission:
                    return True

    return False


@login_required(login_url='login')
def projects(request):
    title = 'Projects'
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
    }

    return render(request, 'projects/projects.html', context=context)


@login_required(login_url='login')
def project_create(request):
    title = 'Create Project'
    stage = 1
    project_per_add = False

    for permission in all_permission(request):
        # Permission add project
        if str(permission['permission']) == 'add' and permission['object_type'] == 'project':
            project_per_add = True
            break

    create_form = ''
    if project_per_add or request.user.is_superuser:
        create_form = ProjectCreateForm()

        if request.method == 'POST':
            create_form = ProjectCreateForm(request.POST)
            if create_form.is_valid():
                print(request.POST)
                new_project = create_form.save()
                # Get info of project manager
                user = UserManagement.objects.get(
                    id=request.POST['project_manager'])
                # Create group full permission for this project
                group = UserGroup(object_type='project', object_id=new_project.id,
                                  name=f"project_{new_project.id}_view_add_change_delete")
                group.save()
                group.permission.set(DJPermission.objects.all())
                # Add full permission for project manager
                user.user_group.add(group)

                # Write log file
                log = UserLogFile(user=request.user, action_code='create',
                                  object_type='project', object_id=new_project.id)
                log.save()

                return redirect('phase_settings', pk_project=new_project.id)
    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect('projects')

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'create_form': create_form,
    }

    return render(request, 'projects/project-create.html', context=context)


@login_required(login_url='login')
def project_update(request, pk_project):
    title = 'Update Project'
    projects = []
    phases = []
    tasks = []
    project_per_change = False

    for permission in all_permission(request):
        # Permission view project
        if str(permission['permission']) == 'view':
            if permission['object_type'] == 'project':
                project = Project.objects.get(id=permission['object_id'])
                if project not in projects:
                    projects.append(project)

                    for phase in Phase.objects.filter(project=project):
                        phases.append(phase)

                        for task in Task.objects.filter(phase=phase):
                            tasks.append(task)

        # Permission change project
        if str(permission['permission']) == 'change':
            if permission['object_type'] == 'project':
                project_per_change = True

    project = Project.objects.get(id=pk_project)
    project_update_form = ''
    phase_form = ''
    # Check permission change project
    if project in projects and project_per_change or request.user.is_superuser:
        phases = Phase.objects.filter(project=pk_project)
        project_update_form = ProjectCreateForm(instance=project)

        PhaseFormSet = inlineformset_factory(Project, Phase,
                                             PhaseCreateForm,
                                             fields=(
                                                 'name', 'start_date',
                                                 'due_date', 'phase_status',
                                                 'phase_finished', 'project',
                                             ), max_num=len(phases))
        phase_form = PhaseFormSet(instance=project)

        if request.method == 'POST':
            project_update_form = ProjectCreateForm(
                request.POST, instance=project)
            old_data = {
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'priority': project.priority,
                'start_date': project.start_date,
                'due_date': project.due_date,
                'customer': project.customer.username,
                'project_manager': project.project_manager.username,
            }

            if project_update_form.is_valid():
                if project_update_form.has_changed():
                    new_project = project_update_form.save()

                    # Write log file
                    log = UserLogFile(user=request.user, action_code='change',
                                      object_type='project', object_id=new_project.id, change_message=old_data)
                    log.save()
                    messages.add_message(
                        request, messages.SUCCESS, "Project was updated.")
                else:
                    messages.add_message(
                        request, messages.WARNING, "There\'s nothing to change.")
                return redirect('projects')
    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    context = {
        'brand': brand,
        'title': title,
        'project_update_form': project_update_form,
        'phases': phases,
        'phase_form': phase_form,
    }
    return render(request, 'projects/project-update.html', context=context)


@login_required(login_url='login')
def project_delete(request, pk_project):
    title = 'Delete Project'
    projects = []
    project_per_delete = False

    for permission in all_permission(request):
        # Permission view project
        if str(permission['permission']) == 'view':
            if permission['object_type'] == 'project':
                project = Project.objects.get(id=permission['object_id'])
                if project not in projects:
                    projects.append(project)

        # Permission delete project
        if str(permission['permission']) == 'delete':
            if permission['object_type'] == 'project':
                project_per_delete = True

    project = Project.objects.get(id=pk_project)
    if project in projects and project_per_delete or request.user.is_superuser:
        if request.method == 'POST':
            old_data = {
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'priority': project.priority,
                'start_date': project.start_date,
                'due_date': project.due_date,
                'customer': project.customer.username,
                'project_manager': project.project_manager.username,
            }

            # Write log file
            log = UserLogFile(user=request.user, action_code='delete',
                              object_type='project', object_id=project.id, change_message=old_data)
            log.save()

            project.delete()

            return redirect('projects')
    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    context = {
        'brand': brand,
        'title': title,
        'project': project,
    }
    return render(request, 'projects/project-delete.html', context=context)


@login_required(login_url='login')
def phase_settings(request, pk_project):
    title = 'Phase Settings'
    stage = 2

    projects = []
    phase_per_change = False
    phase_per_add = False
    phase_per_delete = False

    if request.user.is_superuser:
        phase_per_change = True
        phase_per_add = True
        phase_per_delete = True
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'view':
                # Permission view project
                if permission['object_type'] == 'project':
                    project = Project.objects.get(id=permission['object_id'])
                    if project not in projects:
                        projects.append(project)

            if str(permission['permission']) == 'change':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    phase_per_change = True

            if str(permission['permission']) == 'add':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    phase_per_add = True

            if str(permission['permission']) == 'delete':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    phase_per_delete = True

    project = Project.objects.get(id=pk_project)
    list_phase = ''
    formset = ''
    all_phases_formset = ''

    if project in projects or request.user.is_superuser:
        list_phase = CustomPhase.objects.all()

        all_phases_formset = modelformset_factory(CustomPhase,
                                                  form=ListPhaseForm,
                                                  can_delete=True,
                                                  )

        if request.method == 'POST':
            if 'save-phase-settings' in request.POST:
                formset = all_phases_formset(data=request.POST or None)
                if formset.has_changed():
                    if formset.is_valid():
                        formset.save()
                        messages.add_message(
                            request, messages.SUCCESS, 'Phase settings updated.')
                    else:
                        messages.add_message(
                            request, messages.ERROR, formset.errors)
                        print(formset.errors)
                else:
                    messages.add_message(
                        request, messages.WARNING, 'There\'s nothing to change.')

            if 'add-phase-to-project' in request.POST:
                for phase_item in list_phase:
                    if phase_item.selected:
                        try:
                            phase_exists = Phase.objects.get(
                                name=phase_item.phase_name, project=project)
                        except:
                            phase_exists = None
                        # Check phase name exist in table Phase of Project

                        if not phase_exists:
                            new_phase = Phase(
                                name=phase_item.phase_name, project=project)
                            try:
                                new_phase.save()
                                messages.add_message(
                                    request, messages.SUCCESS, f"Phase {new_phase} added.")
                            except Exception as e:
                                messages.add_message(
                                    request, messages.ERROR, e)
                        else:
                            messages.add_message(
                                request, messages.ERROR, f"Exists phase: {phase_exists}. Choose another name.")

                return redirect('phase_edit', pk_project=pk_project)

    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'list_phase': list_phase,
        'project': project,
        'all_phases': all_phases_formset,
        'formset': formset,
        'phase_per_add': phase_per_add,
        'phase_per_change': phase_per_change,
        'phase_per_delete': phase_per_delete,
    }
    return render(request, 'projects/phase-settings.html', context=context)


@login_required(login_url='login')
def phase_edit(request, pk_project):
    title = 'Phase Edit'
    stage = 3
    phase_per_add = False
    phase_per_delete = False

    projects = []
    phase_view = []
    phase_change = []  # Need permission change to each phase
    phases = []
    phase_form = ''
    project = Project.objects.get(id=pk_project)
    if request.user.is_superuser:
        phase_per_add = True
        phase_per_delete = True
        phases = Phase.objects.filter(project=project)
        phase_change = phases
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'view':
                # Permission view project
                if permission['object_type'] == 'project':
                    _project = Project.objects.get(id=permission['object_id'])
                    if _project not in projects:
                        projects.append(_project)

                # Permission view phase
                if permission['object_type'] == 'phase':
                    phase = Phase.objects.get(id=permission['object_id'])
                    if phase not in phase_view:
                        phase_view.append(phase)
                        project = phase.project

                        if project not in projects:
                            projects.append(project)

            # Permission add phase
            if str(permission['permission']) == 'add':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    phase_per_add = True

            # Permission change phase
            if str(permission['permission']) == 'change':
                if permission['object_type'] == 'project':
                    phase_change = Phase.objects.filter(project=project)
                if permission['object_type'] == 'phase':
                    phase = Phase.objects.get(id=permission['object_id'])
                    if phase not in phase_change:
                        phase_change.append(phase)

            # Permission delete phase
            if str(permission['permission']) == 'delete':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    phase_per_delete = True

    # print('phase_change', phase_change)

    if project in projects or request.user.is_superuser:
        # Check if project owner or admin
        for phase in phase_view:
            if phase.project == project:
                phases.append(phase)
        # print(phases)

        PhaseFormSet = inlineformset_factory(Project, Phase,
                                             PhaseCreateForm,
                                             fields='__all__',
                                             max_num=len(phase_change))
        phase_form = PhaseFormSet(instance=project, queryset=Phase.objects.filter(
            id__in=[phase.id for phase in phase_change]))

        if request.method == 'POST':
            if 'update-phase' in request.POST:
                form = PhaseFormSet(request.POST or None, instance=project)
                if form.has_changed():
                    if form.is_valid():
                        form.save()
                        messages.add_message(
                            request, messages.SUCCESS, 'Phase updated successfully.')
                    else:
                        messages.add_message(
                            request, messages.ERROR, form.error)
                else:
                    messages.add_message(
                        request, messages.WARNING, 'There\'s nothing to change.')
                return redirect('phase_edit', project.id)

    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phases': phases,
        'phase_form': phase_form,
        'phase_per_add': phase_per_add,
        'phase_per_delete': phase_per_delete,
        'phase_change': phase_change,
    }
    return render(request, 'projects/phase-edit.html', context=context)


@login_required(login_url='login')
def task_settings(request, pk_project, pk_phase):
    title = 'Task Settings'
    stage = 4
    project = Project.objects.get(id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    list_task = CustomTask.objects.all()

    all_tasks_formset = modelformset_factory(CustomTask,
                                             form=ListTaskForm,
                                             can_delete=True)
    formset = ''

    if request.method == 'POST':
        if 'save-task-settings' in request.POST:
            formset = all_tasks_formset(data=request.POST or None)

            if formset.is_valid():
                formset.save()
                messages.add_message(
                    request, messages.SUCCESS, 'Task settings updated.')
            else:
                messages.add_message(
                    request, messages.ERROR, formset.errors)
                print(formset.errors)

        if 'add-task-to-phase' in request.POST:
            for task_item in list_task:
                if task_item.selected:
                    try:
                        task_exists = Task.objects.get(
                            name=task_item.task_name, phase=phase)
                    except:
                        task_exists = None

                    if not task_exists:
                        new_task = Task(
                            name=task_item.task_name, phase=phase)
                        try:
                            new_task.save()
                            messages.add_message(
                                request, messages.SUCCESS, f"Task {new_task} added.")
                        except Exception as e:
                            messages.add_message(request, messages.ERROR, e)
                    else:
                        messages.add_message(
                            request, messages.ERROR, f"Task named <b> {task_exists.name} </b> \
                            already exists in table Phase. Choose another name.", extra_tags='safe')

            return redirect('task_views', project.id, phase.id)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phase': phase,
        'list_task': list_task,
        'all_tasks': all_tasks_formset,
        'formset': formset,
    }
    return render(request, 'projects/task-settings.html', context=context)


@login_required(login_url='login')
def task_views(request, pk_project, pk_phase):
    title = 'Task View'
    stage = 4
    task_per_add = False
    task_delete = []

    projects = []
    phases = []
    tasks = []
    task_change = []  # Need permission change to each phase

    project = Project.objects.get(id=pk_project)
    phase = Phase.objects.get(id=pk_phase)

    if request.user.is_superuser:
        task_per_add = True
        tasks = Task.objects.filter(phase=phase)
        task_change = tasks
        task_delete = tasks
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'view':
                # Permission view project
                if permission['object_type'] == 'project':
                    _project = Project.objects.get(id=permission['object_id'])
                    if _project not in projects:
                        projects.append(_project)

                        for _phase in Phase.objects.filter(project=project):
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

                        for _task in Task.objects.filter(phase=_phase):
                            if _task not in tasks:
                                tasks.append(_task)

                # Permission view task
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in tasks:
                        tasks.append(_task)

            # Permission add task
            if str(permission['permission']) == 'add':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    task_per_add = True

            # Permission change task
            if str(permission['permission']) == 'change':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    task_change = Task.objects.filter(phase=phase)
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in task_change:
                        task_change.append(_task)

            # Permission delete task
            if str(permission['permission']) == 'delete':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    task_delete = Task.objects.filter(phase=phase)
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in task_delete:
                        task_delete.append(_task)

    if tasks or request.user.is_superuser:
        pass
    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phase': phase,
        'tasks': tasks,
        'task_per_add': task_per_add,
        'task_delete': task_delete,
        'task_change': task_change,
    }
    return render(request, 'projects/task-views.html', context=context)


@login_required(login_url='login')
def task_edits(request, pk_project, pk_phase, pk_task):
    title = 'Edit Task'
    stage = 5

    task_per_add = False
    task_per_change = False
    task_change = []
    task_delete = []

    projects = []
    phases = []
    tasks = []

    project = Project.objects.get(id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    task = get_object_or_404(Task, id=pk_task, phase=phase)

    if request.user.is_superuser:
        task_per_add = True
        task_per_change = True
        tasks = Task.objects.filter(phase=phase)
        task_change = tasks
        task_delete = tasks
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'view':
                # Permission view project
                if permission['object_type'] == 'project':
                    _project = Project.objects.get(id=permission['object_id'])
                    if _project not in projects:
                        projects.append(_project)

                    for _phase in Phase.objects.filter(project=project):
                        if _phase not in phases:
                            phases.append(_phase)
                        for _task in Task.objects.filter(phase=phase):
                            if _task not in tasks:
                                tasks.append(_task)
                # Permission view phase
                if permission['object_type'] == 'phase':
                    _phase = Phase.objects.get(id=permission['object_id'])
                    if _phase not in phases:
                        phases.append(_phase)

                        for _task in Task.objects.filter(phase=_phase):
                            tasks.append(_task)

                # Permission view task
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in tasks:
                        tasks.append(_task)

            # Permission add task
            if str(permission['permission']) == 'add':
                task_per_add = True

            # Permission change task
            if str(permission['permission']) == 'change':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    task_change = Task.objects.filter(phase=phase)
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in task_change:
                        task_change.append(_task)

            # Permission delete task
            if str(permission['permission']) == 'delete':
                if permission['object_type'] == 'project' or permission['object_type'] == 'phase':
                    task_delete = Task.objects.filter(phase=phase)
                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in task_delete:
                        task_delete.append(_task)

    task_form = TaskCreateForm(instance=task)
    file_form = FileCreateForm(instance=task)
    if task in task_change:
        task_per_change = True

        if request.method == 'POST':
            if 'update-task' in request.POST:
                form = TaskCreateForm(request.POST or None, instance=task)
                tf = TaskFiles()

                # Handle task form
                if form.has_changed():
                    if form.is_valid():
                        f = form.save(commit=False)
                        if f.task_finished == True:
                            f.date_finished = timezone.now()
                        f.save()

                        messages.add_message(
                            request, messages.SUCCESS, 'Task updated successfully.')
                    else:
                        messages.add_message(
                            request, messages.ERROR, form.errors)

                # Handle file form
                try:
                    print(request.POST)
                    uploaded_file = request.FILES.get('attachment')
                    project_name = project.name.replace(' ', '-')
                    phase_name = phase.name.replace(' ', '-')
                    task_name = task.name.replace(' ', '-')
                    location = f"{project_name}/{phase_name}/{task_name}"

                    file_name = default_storage.save(
                        f"{location}/{uploaded_file.name}", uploaded_file)
                    print('file_name', file_name)
                    file_url = default_storage.url(
                        f"{location}/{uploaded_file.name}")
                    print('file_url', file_url)

                    tf.name = file_name.split('/')[-1]
                    tf.attachment = f"{settings.MEDIA_URL}{file_name}"
                    tf.url = f"{settings.MEDIA_URL}{file_name}"
                    tf.task = Task.objects.get(id=pk_task, phase=phase)
                    tf.user = UserManagement.objects.get(id=request.user.id)
                    tf.save()

                    messages.add_message(
                        request, messages.SUCCESS, 'File uploaded.')

                except Exception as err:
                    print(err)

                return redirect('task_edits', project.id, phase.id, task.id)

    # User who have permission upload file
    if task.user_upload:
        if request.user.id == task.user_upload.id:
            if request.method == 'POST':
                if 'update-task' in request.POST:
                    form = TaskCreateForm(request.POST or None, instance=task)
                    tf = TaskFiles()

                    # Handle file form
                    try:
                        print(request.POST)
                        uploaded_file = request.FILES.get('attachment')
                        project_name = project.name.replace(' ', '-')
                        phase_name = phase.name.replace(' ', '-')
                        task_name = task.name.replace(' ', '-')
                        location = f"{project_name}/{phase_name}/{task_name}"

                        file_name = default_storage.save(
                            f"{location}/{uploaded_file.name}", uploaded_file)
                        print('file_name', file_name)
                        file_url = default_storage.url(
                            f"{location}/{uploaded_file.name}")
                        print('file_url', file_url)

                        tf.name = file_name.split('/')[-1]
                        tf.attachment = f"{settings.MEDIA_URL}{file_name}"
                        tf.url = f"{settings.MEDIA_URL}{file_name}"
                        tf.task = Task.objects.get(id=pk_task, phase=phase)
                        tf.user = UserManagement.objects.get(
                            id=request.user.id)
                        tf.save()

                        messages.add_message(
                            request, messages.SUCCESS, 'File uploaded.')

                    except Exception as err:
                        print(err)

                    return redirect('task_edits', project.id, phase.id, task.id)

    # Get attachment of Task
    task_files = TaskFiles.objects.filter(task=pk_task)
    last_file = task_files[len(task_files)-1] if len(task_files) > 0 else 0

    file_formset = inlineformset_factory(Task, TaskFiles,
                                         FileApproveForm,
                                         fields='__all__',
                                         max_num=len(task_files))
    approve_form = file_formset(instance=task)
    if request.method == 'POST':
        if 'btn-approve-file' in request.POST:
            form = file_formset(request.POST, instance=task)

            if form.is_valid():
                f = form.save(commit=False)
                for item in f:
                    if item.file_approved or item.file_rejected:
                        item.date_approved = timezone.now()
                        item.save()
            else:
                print(form.errors)

            messages.add_message(request, messages.SUCCESS,
                                 'Approve file successfully.')
            return redirect('task_edits', project.id, phase.id, task.id)
        print(request.POST)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phase': phase,
        'task': task,
        'task_form': task_form,
        'file_form': file_form,
        'task_files': task_files,
        'last_file': last_file,
        'approve_form': approve_form,

        'task_per_add': task_per_add,
        'task_per_change': task_per_change,
        'task_change': task_change,
        'task_delete': task_delete,
    }
    return render(request, 'projects/task-edits.html', context=context)


@login_required(login_url='login')
def task_delete(request, pk_project, pk_phase, pk_task):
    title = 'Delete Task'
    project = Project.objects.get(id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    task = Task.objects.get(id=pk_task)

    projects = []
    phases = []
    tasks = []
    task_per_delete = False

    if request.user.is_superuser:
        task_per_delete = True
    else:
        for permission in all_permission(request):
            if str(permission['permission']) == 'delete':
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

                if permission['object_type'] == 'phase':
                    _phase = Phase.objects.get(id=permission['object_id'])
                    if _phase not in phases:
                        phases.append(_phase)

                        for _task in Task.objects.filter(phase=_phase):
                            if _task not in tasks:
                                tasks.append(_task)

                if permission['object_type'] == 'task':
                    _task = Task.objects.get(id=permission['object_id'])
                    if _task not in tasks:
                        tasks.append(_task)

        if project in projects or phase in phases or task in tasks:
            task_per_delete = True

    if task_per_delete:
        pass
    else:
        messages.add_message(request, messages.ERROR,
                             "You don't have permissions for this action.")
        return redirect("projects")

    if request.method == 'POST':
        task.delete()
        return redirect('task_views', project.id, phase.id)

    context = {
        'brand': brand,
        'title': title,
        'project': project,
        'phase': phase,
        'task': task,
    }
    return render(request, 'projects/task-delete.html', context=context)

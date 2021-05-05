from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory, modelformset_factory
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
# Create your views here.
from .models import *
from .forms import ProjectCreateForm, PhaseCreateForm, ListPhaseForm, \
    TaskCreateForm, ListTaskForm, FileCreateForm, FileApproveForm

brand = 'DONGJIN VIETNAM J.S.C'


@login_required(login_url='login')
def projects(request):
    title = 'Projects'
    projects = Project.objects.all()
    phases = Phase.objects.all()
    tasks = Task.objects.all()

    context = {
        'brand': brand,
        'title': title,
        'projects': projects,
        'phases': phases,
        'tasks': tasks,
    }

    return render(request, 'projects/projects.html', context=context)


@login_required(login_url='login')
def project_create(request):
    title = 'Create Project'
    stage = 1
    create_form = ProjectCreateForm()
    list_phase = CustomPhase.objects.all()

    if request.method == 'POST':
        create_form = ProjectCreateForm(request.POST)
        if create_form.is_valid():
            new_project = create_form.save()
            return redirect('phase_settings', pk_project=new_project.project_id)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'create_form': create_form,
        'list_phase': list_phase,
    }

    return render(request, 'projects/project-create.html', context=context)


@login_required(login_url='login')
def project_update(request, pk_project):
    title = 'Update Project'
    project = Project.objects.get(project_id=pk_project)
    phases = Phase.objects.filter(project=pk_project)
    project_update_form = ProjectCreateForm(instance=project)
    PhaseFormSet = inlineformset_factory(Project, Phase,
                                         PhaseCreateForm,
                                         fields=(
                                             'phase_name', 'start_date',
                                             'due_date', 'phase_status',
                                             'phase_finished', 'project',
                                         ), max_num=len(phases))
    phase_form = PhaseFormSet(instance=project)

    if request.method == 'POST':
        # print('POST', request.POST)
        project_update_form = ProjectCreateForm(request.POST, instance=project)
        if project_update_form.is_valid():
            project_update_form.save()
            return redirect('projects')

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
    project = Project.objects.get(project_id=pk_project)

    if request.method == 'POST':
        project.delete()
        return redirect('projects')

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
    project = Project.objects.get(project_id=pk_project)
    list_phase = CustomPhase.objects.all()

    all_phases_formset = modelformset_factory(CustomPhase,
                                              form=ListPhaseForm,
                                              can_delete=True,
                                              )
    formset = ''

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
                    request, messages.WARNING, 'There is nothing to change.')

        if 'add-phase-to-project' in request.POST:
            for phase_item in list_phase:
                if phase_item.selected:
                    phase_exists = Phase.objects.filter(
                        phase_name=phase_item.phase_name, project=project)
                    # Check phase name exist in table Phase of Project

                    if not phase_exists:
                        new_phase = Phase(
                            phase_name=phase_item.phase_name, project=project)
                        try:
                            new_phase.save()
                            messages.add_message(
                                request, messages.SUCCESS, f"Phase {new_phase} added.")
                        except Exception as e:
                            messages.add_message(request, messages.ERROR, e)
                    else:
                        messages.add_message(
                            request, messages.ERROR, f"Exists phase: {phase_exists}. Choose another name.")

            return redirect('phase_edit', pk_project=pk_project)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'list_phase': list_phase,
        'project': project,
        'all_phases': all_phases_formset,
        'formset': formset,
    }
    return render(request, 'projects/phase-settings.html', context=context)


@login_required(login_url='login')
def phase_edit(request, pk_project):
    title = 'Phase Edit'
    stage = 3
    project = Project.objects.get(project_id=pk_project)
    phases = Phase.objects.filter(project=project)

    PhaseFormSet = inlineformset_factory(Project, Phase,
                                         PhaseCreateForm,
                                         fields='__all__',
                                         max_num=len(phases))
    phase_form = PhaseFormSet(instance=project)

    if request.method == 'POST':
        if 'update-phase' in request.POST:
            form = PhaseFormSet(request.POST or None, instance=project)
            if form.has_changed():
                if form.is_valid():
                    form.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'Phase updated successfully.')
                else:
                    messages.add_message(request, messages.ERROR, form.error)
            else:
                messages.add_message(
                    request, messages.WARNING, 'There is nothing to change.')
            return redirect('phase_edit', project.project_id)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phases': phases,
        'phase_form': phase_form,
    }
    return render(request, 'projects/phase-edit.html', context=context)


@login_required(login_url='login')
def task_settings(request, pk_project, pk_phase):
    title = 'Task Settings'
    stage = 4
    project = Project.objects.get(project_id=pk_project)
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
                    task_exists = Task.objects.filter(
                        task_name=task_item.task_name, phase=phase)

                    if not task_exists:
                        new_task = Task(
                            task_name=task_item.task_name, phase=phase)
                        try:
                            new_task.save()
                            messages.add_message(
                                request, messages.SUCCESS, f"Task {new_task} added.")
                        except Exception as e:
                            messages.add_message(request, messages.ERROR, e)
                    else:
                        messages.add_message(
                            request, messages.ERROR, f"Task named <b> {task_exists[0].task_name} </b> \
                            already exists in table Phase. Choose another name.", extra_tags='safe')

            return redirect('task_views', project.project_id, phase.id)

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
    project = Project.objects.get(project_id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    tasks = Task.objects.filter(phase=phase)

    context = {
        'brand': brand,
        'title': title,
        'stage': stage,
        'project': project,
        'phase': phase,
        'tasks': tasks,
    }
    return render(request, 'projects/task-views.html', context=context)


@login_required(login_url='login')
def task_edits(request, pk_project, pk_phase, pk_task):
    title = 'Edit Task'
    stage = 5
    project = Project.objects.get(project_id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    task = Task.objects.get(task_id=pk_task, phase=phase)

    task_form = TaskCreateForm(instance=task)
    file_form = FileCreateForm(instance=task)

    if request.method == 'POST':
        if 'update-task' in request.POST:
            form = TaskCreateForm(request.POST or None, instance=task)
            f_form = FileCreateForm(request.FILES, instance=task)
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
                    messages.add_message(request, messages.ERROR, form.errors)

            # Handle file form
            try:
                uploaded_file = request.FILES.get('attachment')
                project_name = project.name.replace(' ', '-')
                phase_name = phase.phase_name.replace(' ', '-')
                task_name = task.task_name.replace(' ', '-')
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
                tf.task = Task.objects.get(task_id=pk_task, phase=phase)
                tf.user = UserManagement.objects.get(id=request.user.id)
                tf.save()

                messages.add_message(
                    request, messages.SUCCESS, 'File uploaded.')

            except Exception as err:
                pass

            return redirect('task_edits', project.project_id, phase.id, task.task_id)

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

            messages.add_message(request, messages.SUCCESS, 'Approve file successfully.')
            return redirect('task_edits', project.project_id, phase.id, task.task_id)

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
    }
    return render(request, 'projects/task-edits.html', context=context)


@login_required(login_url='login')
def task_delete(request, pk_project, pk_phase, pk_task):
    title = 'Delete Task'
    project = Project.objects.get(project_id=pk_project)
    phase = Phase.objects.get(id=pk_phase)
    task = Task.objects.get(task_id=pk_task)

    if request.method == 'POST':
        task.delete()
        return redirect('task_views', project.project_id, phase.id)

    context = {
        'brand': brand,
        'title': title,
        'project': project,
        'phase': phase,
        'task': task,
    }
    return render(request, 'projects/task-delete.html', context=context)

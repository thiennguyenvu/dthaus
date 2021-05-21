from django import forms
from django.forms import ModelForm
from .models import models, Project, Phase, CustomPhase, Task, CustomTask, TaskFiles


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectCreateForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        exclude = ('progress', 'date_finished',)
        widgets = {
            'start_date': DateInput(),
            'due_date': DateInput(),
            'date_finished': DateInput(),
        }


class PhaseCreateForm(ModelForm):
    class Meta:
        model = Phase
        fields = '__all__'
        widgets = {
            'start_date': DateInput(),
            'due_date': DateInput(),
            'description': forms.TextInput(),
        }


class ListPhaseForm(ModelForm):
    class Meta:
        model = CustomPhase
        fields = {'selected', 'phase_name'}
        widgets = {
            'phase_name': forms.TextInput(attrs={'placeholder': 'Add new phase'}),
        }


class ListTaskForm(ModelForm):
    class Meta:
        model = CustomTask
        fields = {'selected', 'task_name'}
        widgets = {
            'task_name': forms.TextInput(attrs={'placeholder': 'Add new task'}),
        }


class TaskCreateForm(ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ('phase', 'date_finished', )
        widgets = {
            'start_date_upload': DateInput(),
            'due_date_upload': DateInput(),
            'start_date_approve': DateInput(),
            'due_date_approve': DateInput(),
            'description': forms.TextInput(),
        }


class FileCreateForm(ModelForm):
    class Meta:
        model = TaskFiles
        fields = '__all__'


class FileApproveForm(ModelForm):
    disabled_fields = ['name', 'url', 'user', 'task', 'date_approved']

    class Meta:
        model = TaskFiles
        fields = '__all__'
        exclude = ('attachment', )

    def __init__(self, *args, **kwargs):
        super(FileApproveForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            for field in self.disabled_fields:
                self.fields[field].disabled = True

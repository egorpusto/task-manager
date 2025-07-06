from django import forms
from .models import Task, Tag
from django_select2 import forms as s2forms


class TagWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ['name__icontains']


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description',
                  'priority', 'status', 'deadline', 'tags']
        widgets = {
            'tags': TagWidget(attrs={
                'data-placeholder': 'Выберите теги...',
                'data-width': '100%'
            }),
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()

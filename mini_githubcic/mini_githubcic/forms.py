from .models import Branch, Project
from django.forms import ModelForm


class BranchForm(ModelForm):

    class Meta:
        model = Branch
        fields = ['name', 'parent_branch']

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = Project.objects.get(id=project_id)
        self.fields['parent_branch'].queryset = Branch.objects.filter(project=project)

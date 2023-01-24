from .models import Branch, Project, Comment
from django.forms import ModelForm


class BranchForm(ModelForm):

    class Meta:
        model = Branch
        fields = ['name', 'parent_branch']

    def __init__(self, project_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project = Project.objects.get(id=project_id)
        self.fields['parent_branch'].queryset = Branch.objects.filter(project=project)


class CommentForm(ModelForm):

    class Meta:
        model = Comment
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

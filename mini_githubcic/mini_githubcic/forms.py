from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from .models import Label, Issue, Branch, PullRequest, Project, Comment, User


class NewIssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(NewIssueForm, self).__init__(*args, **kwargs)

        self.fields['labels'] = ModelMultipleChoiceField(
            widget=CheckboxSelectMultiple(),
            queryset=Label.objects.filter(project=self.project).all(),
            required=False
        )
        self.fields['assigned_to'].queryset = self.project.developers
        self.fields['assigned_to'].required = False
        self.fields['description'].required = False

    class Meta:
        model = Issue
        fields = ['title', 'description', 'assigned_to', 'labels']


class UpdateIssueForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(UpdateIssueForm, self).__init__(*args, **kwargs)

        self.fields['labels'] = ModelMultipleChoiceField(
            widget=CheckboxSelectMultiple(),
            queryset=Label.objects.filter(project=self.project).all(),
            required=False
        )
        self.fields['labels'].required = False
        self.fields['assigned_to'].queryset = self.project.developers
        self.fields['assigned_to'].required = False
        self.fields['description'].required = False

    class Meta:
        model = Issue
        fields = ['title', 'description', 'assigned_to', 'is_open', 'labels']


class UpdateProjectForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(UpdateProjectForm, self).__init__(*args, **kwargs)

        self.fields['developers'] = ModelMultipleChoiceField(
            widget=CheckboxSelectMultiple(),
            queryset=User.objects.filter().all(),
            required=False
        )
        self.fields['description'].required = False

    class Meta:
        model = Project
        fields = ['title', 'description', 'developers', 'visibility', 'licence']


class NewPullRequestForm(ModelForm):

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(NewPullRequestForm, self).__init__(*args, **kwargs)

        self.fields['labels'] = ModelMultipleChoiceField(
            widget=CheckboxSelectMultiple(),
            queryset=Label.objects.filter(project=self.project).all(),
            required=False
        )
        self.fields['source'].queryset = Branch.objects.filter(project=self.project).all()
        self.fields['target'].queryset = Branch.objects.filter(project=self.project).all()
        self.fields['assigned_to'].queryset = self.project.developers
        self.fields['assigned_to'].required = False
        self.fields['description'].required = False

    class Meta:
        model = PullRequest
        fields = ['title', 'description', 'assigned_to', 'source', 'target', 'labels']


class UpdatePullRequestForm(ModelForm):

    class Meta:
        model = PullRequest
        fields = ['title', 'description', 'assigned_to', 'is_open', 'labels']

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(UpdatePullRequestForm, self).__init__(*args, **kwargs)

        self.fields['labels'] = ModelMultipleChoiceField(
            widget=CheckboxSelectMultiple(),
            queryset=Label.objects.filter(project=self.project).all(),
            required=False
        )
        self.fields['assigned_to'].queryset = self.project.developers
        self.fields['assigned_to'].required = False
        self.fields['description'].required = False

    class Meta:
        model = PullRequest
        fields = ['title', 'description', 'assigned_to', 'labels']


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

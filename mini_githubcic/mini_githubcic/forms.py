from django.forms import ModelForm, ModelMultipleChoiceField, CheckboxSelectMultiple
from .models import Label, Issue, Branch, PullRequest


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

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(UpdatePullRequestForm, self).__init__(*args, **kwargs)

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
        fields = ['title', 'description', 'assigned_to', 'labels']

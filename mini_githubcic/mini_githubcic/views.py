from django.apps.registry import apps
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)

from .models import Project, User, Milestone, Issue, Label, Branch, Commit, Visibility, Comment, ReactionType, Reaction

from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.db.models import Q
import uuid
from .forms import BranchForm, CommentForm
import re


def index(request):
    title = apps.get_app_config('mini_githubcic').verbose_name
    return render(request, 'index.html', {"title": title})


def sign_in(request, id=None):
    if request.method == 'GET':
        return render(request, "login.html")
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        try:
            user = User.objects.get(username=username)
            if user.password != password:
                return render(request, "login.html",
                              {"users_error": "User with this username and password does not exist"})

            login(request, user)
            return render(request, "index.html", {"title": "first page"})

        except:
            return render(request, "login.html",
                          {"users_error": "User with this username and password does not exist"})



def sign_out(request):
    logout(request)
    request.session.flush()
    return redirect("login")

class Register(CreateView):
    model = User
    template_name = 'registration.html'
    fields = ['username', 'password']

    def form_valid(self, form):
        if User.objects.filter(username=form.instance.username).exists():
            form.add_error(None, 'Username already in use')
            return super().form_invalid(form)

        return super().form_valid(form)


class ProjectListView(ListView):
    model = Project
    template_name = 'list_projects.html'
    context_object_name = 'projects'
    ordering = ['title']

    def get_queryset(self):
        if(self.request.user.is_authenticated):
            return Project.objects.filter(Q(lead=self.request.user) | Q(visibility=Visibility.PUBLIC) | Q(developers=self.request.user)).distinct()
        else: return Project.objects.filter(visibility=Visibility.PUBLIC)


class IssueListView(ListView):
    model = Issue
    template_name = 'list_issues.html'
    context_object_name = 'issues'
    ordering = ['id']

    def get_context_data(self, *args, **kwargs):
        context = super(IssueListView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=context['project_id']).first()
        context['issues'] = Issue.objects.filter(project__id=context['project_id'])
        return context


class BranchListView(ListView):
    model = Branch
    template_name = 'list_branches.html'
    context_object_name = 'issues'
    ordering = ['id']

    def get_context_data(self, *args, **kwargs):
        context = super(BranchListView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=context['project_id']).first()
        context['branches'] = Branch.objects.filter(project__id=context['project_id'])
        return context


class ProjectCreateView(CreateView):
    model = Project
    template_name = 'new_project.html'
    fields = ['title', 'description', 'licence', 'visibility']

    def form_valid(self, form):
        form.instance.lead = self.request.user
        form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
        if Project.objects.filter(title=form.instance.title).exists():
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)

        return super().form_valid(form)


class IssueCreateView(CreateView):
    model = Issue
    template_name = 'new_issue.html'
    fields = ['title', 'description', 'assigned_to']

    def form_valid(self, form):
        if Issue.objects.filter(title=form.instance.title).exists():
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)

        context = self.get_context_data()
        form.instance.project = context['project']
        form.instance.creator = self.request.user
        form.instance.date_created = timezone.now()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(IssueCreateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context


def new_branch(request, pk):
    project = Project.objects.filter(id=int(pk)).first()
    if not project:
        return redirect('/projects')

    branches = Branch.objects.filter(project=project)
    form = BranchForm(pk)
    obj_dict = {
        'form': form,
        'project': project,
        'branches': branches,
    }

    if request.method == 'POST':
        form_data = BranchForm(pk, request.POST)

        if form_data.is_valid():
            branch = Branch(**form_data.cleaned_data)
            branch.project = project

            if Branch.objects.filter(project_id=branch.project.id, name=branch.name).exists():
                obj_dict['error_add'] = 'Name already in use'
                return render(request, 'new_branch.html', obj_dict)
            else:
                f = Commit.objects.filter(branches__id__in=[branch.parent_branch.id])
                branch.save()
                for c in f:
                    c.branches.add(branch)
                    c.save()

                return redirect('/branches/{}'.format(str(branch.id)))

    return render(request, 'new_branch.html', obj_dict)


def new_comment(request, pk):
    reactions = add_reactions()

    issue = Issue.objects.filter(id=int(pk)).first()
    if not issue:
        return redirect('/projects')

    form = CommentForm()
    comment_list = Comment.objects.filter(task__id=int(pk))
    comments_reactions = []
    for c in comment_list:
        comments_reactions.append({'comment':c, 'reactions':Reaction.objects.filter(comment=c)})

    obj_dict = {
        'comment_form': form,
        'issue': issue,
        'comments': comments_reactions,
        'reactions': reactions
    }

    if request.method == 'POST':
        form_data = CommentForm(request.POST)

        if form_data.is_valid():
            comment = Comment(**form_data.cleaned_data)
            comment.task = issue

            if not request.user.is_authenticated:
                obj_dict['error_add'] = 'User not authenticated'
                return render(request, 'issue_detail.html', obj_dict)
            else:
                comment.writer = request.user
                comment.date_time = timezone.now()
                comment.save()
                return redirect('/issues/{}'.format(pk))

    return render(request, 'issue_detail.html', obj_dict)


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'project_update.html'
    fields = ['title', 'description', 'developers', 'visibility', 'link', 'licence']

    def form_valid(self, form):

        if Project.objects.filter(title=form.instance.title).exists():
            if self.get_object().id != form.instance.id:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)
        return super().form_valid(form)


class IssueUpdateView(UpdateView):
    model = Issue
    template_name = 'issue_update.html'
    fields = ['title', 'description', 'assigned_to', 'is_open']

    def form_valid(self, form):

        if Issue.objects.filter(title=form.instance.title).exists():
            if self.get_object().id != form.instance.id:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)

        return super().form_valid(form)


class BranchUpdateView(UpdateView):
    model = Branch
    template_name = 'branch_update.html'
    fields = ['name']

    def form_valid(self, form):
        proj = Project.objects.filter(id=int(form.instance.project.id)).first()
        if Branch.objects.filter(project=proj,name=form.instance.name).exists():
            form.add_error(None, 'Name already in use')
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(BranchUpdateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context


class CommentUpdateView(UpdateView):
    model = Comment
    template_name = 'comment_update.html'
    fields = ['content']

    def form_valid(self, form):
        if form.instance.content in [None, "", []]:
            form.add_error(None, 'Comment must have content')
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.object.task.id})


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ProjectDetailView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['main_branch'] = Branch.objects.filter(project__id=context['project_id'], name='main').first()
        if context['main_branch'] is None:
            b = Branch(name="main", project=Project.objects.filter(id=int(context['project_id'])).first())
            b.save()
            context['main_branch'] = b

        return context


class IssueDetailView(DetailView):
    model = Issue
    template_name = 'issue_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(IssueDetailView, self).get_context_data(*args, **kwargs)
        context['issue_id'] = self.request.resolver_match.kwargs['pk']
        context['issue'] = Issue.objects.filter(id=context['issue_id']).first()
        context['comments'] = Comment.objects.filter(task__id=context['issue_id'])
        return context


class BranchDetailView(DetailView):
    model = Branch
    template_name = 'branch_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(BranchDetailView, self).get_context_data(*args, **kwargs)
        context['branch_id'] = self.request.resolver_match.kwargs['pk']
        context['branch'] = Branch.objects.filter(id=int(context['branch_id'])).first()
        context['branches'] = Branch.objects.filter(project__id=context['branch'].project.id)
        context['commits'] = Commit.objects.filter(branches__id__in=[context['branch_id']])

        return context


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'project_delete.html'
    success_url = '/projects'

    def test_func(self):
        # TODO check if request sender is project lead
        return True


class BranchDeleteView(DeleteView):
    model = Branch
    template_name = 'branch_delete.html'

    def test_func(self):
        return True

    def get_success_url(self):
        return reverse_lazy('project_branches', kwargs={'pk': self.object.project.id})


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'comment_delete.html'

    def test_func(self):
        return True

    def get_success_url(self):
        return reverse_lazy('issue_detail', kwargs={'pk': self.object.task.id})


class MilestoneListView(ListView):

    model = Milestone
    template_name = 'list_milestones.html'
    context_object_name = 'milestones'
    ordering = ['title']

    def get_context_data(self, *args, **kwargs):
        context = super(MilestoneListView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=context['project_id']).first()
        context['milestones'] = Milestone.objects.filter(project__id=context['project_id'])
        return context

    def get_queryset(self):
        return Milestone.objects.all()


class MilestoneCreateView(CreateView):
    model = Milestone
    template_name = 'new_milestone.html'
    fields = ['title', 'description', 'due_date', 'is_open']

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.project = context['project']
        form.instance.lead = self.request.user
        form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
        if len(Milestone.objects.filter(title=form.instance.title)) != 0:
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(MilestoneCreateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context

class MilestoneUpdateView(UpdateView):
    model = Milestone
    template_name = 'milestone_update.html'

    fields = ['title', 'description', 'due_date', 'is_open']

    def form_valid(self, form):
        if len(Milestone.objects.filter(title=form.instance.title)) != 0: 
            if self.get_object().title != form.instance.title:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)

        return super().form_valid(form)


class MilestoneDetailView(DetailView):
    model = Milestone
    template_name = 'milestone_detail.html'


class MilestoneDeleteView(DeleteView):
    model = Milestone
    template_name = 'milestone_delete.html'

    def get_success_url(self):
        return reverse_lazy('list_milestones', kwargs={'pk': self.object.project.id})

    def test_func(self):
        # TODO check if request sender is project lead
        return True


class IssueDeleteView(DeleteView):
    model = Issue
    template_name = 'issue_delete.html'

    def get_success_url(self):
        return reverse_lazy('project_issues', kwargs={'pk': self.object.project.id})

    def test_func(self):
        # TODO check if request sender is project lead
        return True


def issue_state_toggle(request, pk=None):
    if request.method == 'GET':
        issue = Issue.objects.get(id=pk)
        if issue.is_open:
            issue.is_open = False
        else:
            issue.is_open = True
        issue.save()
        return redirect(issue)


def milestone_close(request, pk=None):
    if request.method == 'GET':
        milestone = Milestone.objects.get(id=pk)
        milestone.is_open = not milestone.is_open
        milestone.save()
        return redirect(milestone)


def toggle_reaction(request, pk=None, rid=None):
    c = Comment.objects.filter(id=pk).first()
    if request.method == 'GET':
        reaction_list = Reaction.objects.filter(type=rid, comment__id=pk, user__id=request.user.id)
        if len(reaction_list) != 0:
            reaction_list.first().delete()
        else:
            new_reaction = Reaction(type=rid, comment=c, user=request.user)
            new_reaction.save()
        return redirect('/issues/{}'.format(c.task.id))


class LabelListView(ListView):
    model = Label
    template_name = 'list_labels.html'
    template_name = 'list_labels.html'
    context_object_name = 'labels'
    ordering = ['name']

    def get_context_data(self, *args, **kwargs):
        context = super(LabelListView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context

    def get_queryset(self):
        return Label.objects.all()

class LabelCreateView(CreateView):
    model = Label
    template_name = 'new_label.html'
    fields = ['name', 'description', 'color']

    def get_form(self, form_class=None):
        form = super(LabelCreateView, self).get_form(form_class)
        form.fields['description'].required = False
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.project = context['project']

        if Label.objects.filter(name=form.instance.name, project_id=form.instance.project.id).exists():
            form.add_error(None, 'Name already in use')
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(LabelCreateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context

class LabelUpdateView(UpdateView):
    model = Label
    template_name = 'label_update.html'
    fields = ['name', 'description', 'color']

    def get_form(self, form_class=None):
        form = super(LabelUpdateView, self).get_form(form_class)
        form.fields['description'].required = False
        return form

    def form_valid(self, form):
        if Label.objects.filter(name=form.instance.name, project_id=form.instance.project.id).exists():
            if self.get_object().name != form.instance.name:
                form.add_error(None, 'Name already in use')
                return super().form_invalid(form)

        return super().form_valid(form)

class LabelDetailView(DetailView):
    model = Label
    template_name = 'label_detail.html'


class LabelDeleteView(DeleteView):
    model = Label
    template_name = 'label_delete.html'

    def get_success_url(self):
        return reverse_lazy('list_labels', kwargs={'pk': self.object.project.id})


class ProfilePreview(DetailView):
    model = User
    template_name = 'profile_preview.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    
    def get_context_data(self, *args, **kwargs):
        context = super(ProfilePreview, self).get_context_data(*args, **kwargs)
        context['user'] = User.objects.filter(username=self.request.resolver_match.kwargs['username']).first()
        context['projects'] = Project.objects.filter(Q(lead=context['user']) & Q(visibility=Visibility.PUBLIC)).all()
        context['commits'] = Commit.objects.filter(author=context['user']).filter(branches__project__visibility=Visibility.PUBLIC).distinct()
        return context


class CommitCreateView(CreateView):
    model = Commit
    template_name = 'new_commit.html'
    fields = ['log_message', 'branches', 'parents']
    # todo: filter branches and commits by project

    def get_form(self, form_class=None):
        form = super(CommitCreateView, self).get_form(form_class)
        form.fields['log_message'].required = True
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.author = self.request.user
        form.instance.date_time = timezone.now()
        form.instance.hash = str(uuid.uuid4().hex) # todo izbaciti i linkovati sa pravim hesom ili ne koristiti uopste
        if form.is_valid:
            new_commit = form.save()
            if len(form.instance.parents.all()) > 2:
                form.add_error(None, 'Commit cannot have more than 2 parent commits')
                new_commit.delete()
                return super().form_invalid(form)
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(CommitCreateView, self).get_context_data(*args, **kwargs)
        context['branch_id'] = self.request.resolver_match.kwargs['pk']
        return context


class CommitDetailView(DetailView):
    model = Commit
    template_name = 'commit_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CommitDetailView, self).get_context_data(*args, **kwargs)
        context['parents'] = self.get_object().parents.all()
        context['branches'] = self.get_object().branches.all()
        return context


def add_reactions():
    reactions = []
    reactions.append({'type': 'LIKE',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f44d.png', 'emoji': '👍'})
    reactions.append({'type': 'DISLIKE',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f44e.png', 'emoji': '👎'})
    reactions.append({'type': 'SMILE',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f389.png', 'emoji': '😄'})
    reactions.append({'type': 'TADA',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f604.png', 'emoji': '🎉'})
    reactions.append({'type': 'THINKING_FACE',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f604.png', 'emoji': '😕'})
    reactions.append({'type': 'HEART',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/2764.png', 'emoji': '❤'})
    reactions.append({'type': 'ROCKET',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f680.png', 'emoji': '🚀'})
    reactions.append({'type': 'EYES',
                      'link': 'https://github.githubassets.com/images/icons/emoji/unicode/1f440.png', 'emoji': '👀'})
    return reactions


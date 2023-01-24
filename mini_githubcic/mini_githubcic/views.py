import inspect
import json

import markdown
import requests
import copy
from django.apps.registry import apps
from django.core import serializers
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

from .github_api.service import search_repositories_by_user, get_all_visible_repositories_by_user, \
    get_specific_repository, get_specific_repository_readme, get_repository_tree, get_file_content, get_tree_recursively, \
    get_commit_changes, get_all_commits_for_branch
from .github_api.utils import send_github_req, get_access_token, decode_base64_file
from .models import Project, User, Milestone, Issue, Label, Branch, Commit, Visibility, Notification

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout
from django.db.models import Q
import uuid

from django.conf import settings


def index(request):
    title = apps.get_app_config('mini_githubcic').verbose_name
    return render(request, 'index.html', {"title": title})


def sign_in(request, id=None):
    if request.method == 'GET':
        context = {
            "github_oauth_url": "https://github.com/login/oauth/authorize?client_id=" + settings.GITHUB_CLIENT_ID + "&scope=repo%2Cuser"}
        return render(request, "login.html", context)
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
        if (self.request.user.is_authenticated):
            return Project.objects.filter(Q(lead=self.request.user) | Q(visibility=Visibility.PUBLIC) | Q(
                developers=self.request.user)).distinct()
        else:
            return Project.objects.filter(visibility=Visibility.PUBLIC)


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
        make_notification(context['project'], "issue")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(IssueCreateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context


class BranchCreateView(CreateView):
    model = Branch
    template_name = 'new_branch.html'
    fields = ['name', 'parent_branch']

    def form_valid(self, form):
        context = self.get_context_data()
        form.instance.project = context['project']
        if Branch.objects.filter(project_id=form.instance.project.id, name=form.instance.name).exists():
            form.add_error(None, 'Name already in use')
            return super().form_invalid(form)

        f = Commit.objects.filter(branches__id__in=[form.instance.parent_branch.id])
        self.object = form.save()
        for c in f:
            c.branches.add(self.object)
            c.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        context = super(BranchCreateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        context['branches'] = Branch.objects.filter(project__id=context['project_id'])
        # self.fields['sel1'].choices = [(b.id, b.name, b) for b in context['branches']] TODO filter select vals

        return context


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
        if Branch.objects.filter(project=proj, name=form.instance.name).exists():
            form.add_error(None, 'Name already in use')
            return super().form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(BranchUpdateView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context


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
        # TODO check if request sender is developer on the project
        return True

    def get_success_url(self):
        return reverse_lazy('project_branches', kwargs={'pk': self.object.project.id})


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
        context['commits'] = Commit.objects.filter(author=context['user']).filter(
            branches__project__visibility=Visibility.PUBLIC).distinct()
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
        form.instance.hash = str(uuid.uuid4().hex)  # todo izbaciti i linkovati sa pravim hesom ili ne koristiti uopste
        if form.is_valid:
            new_commit = form.save()

            if len(form.instance.parents.all()) > 2:
                form.add_error(None, 'Commit cannot have more than 2 parent commits')
                new_commit.delete()
                return super().form_invalid(form)
            make_notification(new_commit.branches.all()[0].project, "commit")
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(CommitCreateView, self).get_context_data(*args, **kwargs)
        context['branch_id'] = self.request.resolver_match.kwargs['pk']
        return context

class StarredProjectListView(ListView):
    model = Project
    template_name = 'list_starred_project.html'
    context_object_name = 'projects'
    ordering = ['title']

    def get_context_data(self, *args, **kwargs):
        context = super(StarredProjectListView, self).get_context_data(*args, **kwargs)
        context['user'] = User.objects.filter(username=self.request.resolver_match.kwargs['username']).first()
        context['projects'] = Project.objects.filter(starred=context['user'])
        print(context['projects'])
        return context

def starr_project(request, pk=None, username=None):
    if request.method == 'GET':
        project = Project.objects.get(id=pk)
        user = User.objects.get(username=username)
        project.starred.add(user)
        project.save()
        return redirect(project)

def unstarr_project(request, pk=None, username=None):
    if request.method == 'GET':
        project = Project.objects.get(id=pk)
        user = User.objects.get(username=username)
        project.starred.remove(user)
        project.save()
        return redirect('../../projects')

def watch_project(request, pk=None, username=None):
    if request.method == 'GET':
        project = Project.objects.get(id=pk)
        user = User.objects.get(username=username)
        project.watched.add(user)
        project.save()
        return redirect(project)

def unwatch_project(request, pk=None, username=None):
    if request.method == 'GET':
        project = Project.objects.get(id=pk)
        user = User.objects.get(username=username)
        project.watched.remove(user)
        project.save()
        return redirect('../../projects')

class WatchedProjectListView(ListView):
    model = Project
    template_name = 'list_watched_project.html'
    context_object_name = 'projects'
    ordering = ['title']

    def get_context_data(self, *args, **kwargs):
        context = super(WatchedProjectListView, self).get_context_data(*args, **kwargs)
        context['user'] = User.objects.filter(username=self.request.resolver_match.kwargs['username']).first()
        context['projects'] = Project.objects.filter(watched=context['user'])
        print(context['projects'])
        return context

class CommitDetailView(DetailView):
    model = Commit
    template_name = 'commit_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super(CommitDetailView, self).get_context_data(*args, **kwargs)
        context['parents'] = self.get_object().parents.all()
        context['branches'] = self.get_object().branches.all()
        return context


class MyNotificationsListView(ListView):
    model = Notification
    template_name = 'list_notifications.html'
    context_object_name = 'notifications'
    ordering = ['project_id']

    def get_context_data(self, *args, **kwargs):
        context = super(MyNotificationsListView, self).get_context_data(*args, **kwargs)
        context['user'] = User.objects.filter(username=self.request.resolver_match.kwargs['username']).first()
        context['notifications'] = Notification.objects.filter(user=context['user'])
        return context

def make_notification(project, type_notification):
    users = project.watched
    for user in users.all():
        message = f"New {type_notification} is made on project {project.title}"
        notification = Notification(project=project, user=user, is_reded=False, message=message)
        notification.save()

def fork_project(request, pk=None, username=None):
    # tj koliko u dublinu da kopiram
    project = Project.objects.filter(id=pk)[0]
    if project.visibility == 'PUBLIC':
        if project.number_of_forked_project is None:
            project.number_of_forked_project = 0
        project.number_of_forked_project +=1
        project.save()
        user = User.objects.filter(username=username)[0]
        new_project = Project(title = project.title,
                              licence = project.licence,
                              description = project.description,
                              visibility = project.visibility,
                              link= project.link,
                              lead = user, fork_parent= project)
        new_project.save()
        saved_project = Project.objects.filter(title=new_project.title, lead = new_project.lead)[0]
        return redirect('../../projects/'+str(saved_project.id))

def changes(request, username=None, repo=None, commitsha=None):
   # repo_info = get_commit_changes(request, username, repo,commitsha)
    repo_info = get_commit_changes(request, 'isidora-stanic', 'uks', '59e3d110bf4bfd5ec22c18193421942a6a56e2ac')
    context = {'repo_info': repo_info}

    for f in repo_info["files"]:
        if "patch" in f:
            content = f["patch"].splitlines()
            f["patch"] = copy.deepcopy(content)
    return render(request, 'file_changes.html', context)


def github_auth_test(request, username):
    # repo_info = search_repositories_by_user(request, username) # todo request.user.username when connected to github
    repo_info = get_all_visible_repositories_by_user(request, username)
    # repo_info = get_specific_repository(request, username, "uks")
    context = {'repo_info': repo_info}
    return render(request, 'test_github_auth.html', context)


def github_get_specific_repo(request, username, repo):
    # repo_info = search_repositories_by_user(request, username) # todo request.user.username when connected to github
    # repo_info = get_all_visible_repositories_by_user(request, username)
    repo_info = get_specific_repository(request, username, repo)
    readme = get_specific_repository_readme(request, username, repo)
    readme_content = markdown.markdown(decode_base64_file(readme['content']))

    tree = get_repository_tree(request, username, repo)

    context = {'repo_info': repo_info, 'readme': readme, 'readme_content': readme_content, 'tree': tree}
    return render(request, 'github_get_specific_repo.html', context)


def github_get_repo_tree_branch(request, username, repo, branch):
    repo_info = get_specific_repository(request, username, repo)
    tree = get_repository_tree(request, username, repo, branch)
    context = {'repo_info': repo_info, 'tree': tree}
    return render(request, 'github_get_specific_repo.html', context)


def github_get_repo_subtree(request, username, repo, path):
    repo_info = get_specific_repository(request, username, repo)
    tree = get_file_content(request, username, repo, path)
    context = {'repo_info': repo_info, 'tree': tree}
    return render(request, 'github_get_specific_repo.html', context)


def github_get_repo_tree_branch_fof(request, username, repo, path):
    repo_info = get_specific_repository(request, username, repo)
    content = get_file_content(request, username, repo, path)
    context = {'repo_info': repo_info, 'tree': content, 'content': markdown.markdown(decode_base64_file(content['content']))}
    return render(request, 'github_get_specific_file.html', context)


def get_full_tree(request, username, repo, branch):
    repo_info = get_specific_repository(request, username, repo)
    tree = get_tree_recursively(request, username, repo, branch)
    context = {'repo_info': repo_info, 'tree': tree}
    return render(request, 'github_get_full_repo.html', context)



def after_auth(request):
    """
    This view runs when the user authorizes this app to use all the account and repository info
    """
    request_token = request.GET.get('code')
    response = get_access_token(request_token)
    # insert access token into session
    request.session['access_token'] = response.json()['access_token']
    return redirect('/')


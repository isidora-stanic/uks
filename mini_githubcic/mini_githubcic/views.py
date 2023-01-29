from datetime import datetime

from itertools import chain
import markdown

#import requests
import copy
from django.apps.registry import apps
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.timezone import timedelta
from django.views.defaults import page_not_found
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)



from .util import *
from .github_api.service import *
from .github_api.utils import send_github_req, get_access_token, decode_base64_file
from .models import *
from .forms import *

from django.urls import reverse_lazy

from django.contrib.auth import login, logout
from django.db.models import Q
import uuid

from django.conf import settings


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
        if self.request.user.is_authenticated:
            return Project.objects.filter(Q(lead=self.request.user) | Q(visibility=Visibility.PUBLIC) | Q(developers=self.request.user)).distinct()
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
    context_object_name = 'branches'
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
        #form.instance.developers.push(self.request.user)
        form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
        if Project.objects.filter(title=form.instance.title).exists():
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)

        return super().form_valid(form)


class IssueCreateView(CreateView):
    model = Issue
    template_name = 'new_issue.html'
    form_class = NewIssueForm

    def form_valid(self, form):
        if Issue.objects.filter(title=form.instance.title).exists():
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)

        context = self.get_context_data()
        form.instance.project = context['project']
        form.instance.creator = self.request.user
        form.instance.date_created = timezone.now()
        super().form_valid(form)
        
        Event.save(CreateEvent(task=self.object, author=self.request.user, created_entity_type='Issue'))
        
        make_notification(context['project'], "issue")
        
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(IssueCreateView, self).get_context_data(**kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context

    def get_form_kwargs(self):
        kwargs = super(IssueCreateView, self).get_form_kwargs()
        kwargs['project'] = Project.objects.filter(id=int(self.kwargs['pk'])).first()
        return kwargs


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

    events = sorted(chain(CreateEvent.objects.filter(task=issue).all(), UpdateEvent.objects.filter(task=issue).all(), \
        LabelApplication.objects.filter(task=issue).all()), key=lambda instance: instance.date_time)

    obj_dict = {
        'comment_form': form,
        'issue': issue,
        'comments': comments_reactions,
        'reactions': reactions,
        'events' : events
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
                comment.author = request.user
                comment.date_time = timezone.now()
                comment.save()
                return redirect('/issues/{}'.format(pk))

    return render(request, 'issue_detail.html', obj_dict)


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'project_update.html'
    form_class = UpdateProjectForm

    def form_valid(self, form):

        if Project.objects.filter(title=form.instance.title).exists():
            if self.get_object().id != form.instance.id:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)
        return super().form_valid(form)


class IssueUpdateView(UpdateView):
    model = Issue
    template_name = 'issue_update.html'
    form_class = UpdateIssueForm

    def form_valid(self, form):

        if Issue.objects.filter(title=form.instance.title).exists():
            if self.get_object().id != form.instance.id:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)

        old_issue = Issue.objects.filter(id=form.instance.id).first()
        old_labels = list(old_issue.labels.all()).copy()

        super().form_valid(form)
        diff = find_differences(old_issue, self.object)
        for f in diff:
            Event.save(UpdateEvent(task=self.object, field_name=f[0], old_content=getattr(old_issue, f[0]), new_content=str(f[1]), author=self.request.user))
        
        
        if(old_labels != list(self.object.labels.all())):
            apply_event = LabelApplication(task=self.object,  author=self.request.user)
            Event.save(apply_event)
            apply_event.applied_labels.set(self.object.labels.all())
            Event.save(apply_event)
            
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(IssueUpdateView, self).get_context_data(**kwargs)
        issue = Issue.objects.filter(id=int(self.request.resolver_match.kwargs['pk'])).first()
        context['project_id'] = issue.project.id
        context['project'] = issue.project
        return context

    def get_form_kwargs(self):
        kwargs = super(IssueUpdateView, self).get_form_kwargs()
        issue = Issue.objects.filter(id=int(self.request.resolver_match.kwargs['pk'])).first()
        kwargs['project'] = issue.project
        return kwargs


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
        context['repo_owner'] = self.get_object().link.split("https://github.com/")[1].split("/")[0]
        context['repo_name'] = self.get_object().link.split("https://github.com/")[1].split("/")[1].replace(".git", "")
        if self.request.user.is_authenticated and self.request.user.access_token:
            repo_info = get_specific_repository(self.request, context['repo_owner'], context['repo_name'])
            # repo_info = get_specific_repository(request, username, "uks")
            if isinstance(repo_info, dict) and 'message' in repo_info.keys():
                context['repo_exists'] = False
            else:
                context['repo_exists'] = True
        else:
            context['repo_exists'] = False

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
        if (form.instance.due_date - datetime.now(timezone.utc)).days < 0:
            form.add_error(None, 'Day is before today')
            return super().form_invalid(form)
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
            Event.save(UpdateEvent(task=issue, field_name='is_open', old_content='true', new_content='false', author=request.user))
        else:
            issue.is_open = True
            Event.save(UpdateEvent(task=issue, field_name='is_open', old_content='false', new_content='true', author=request.user))
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
    link = ''
    if Issue.objects.filter(id=c.task.id):
        link = '/issues/{}'
    else:
        link = '/pull/requests/{}'
    if request.method == 'GET':
        reaction_list = Reaction.objects.filter(type=rid, comment__id=pk, user__id=request.user.id)
        if len(reaction_list) != 0:
            reaction_list.first().delete()
        else:
            new_reaction = Reaction(type=rid, comment=c, user=request.user)
            new_reaction.save()
        return redirect(link.format(c.task.id))


class LabelListView(ListView):
    model = Label
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
    
    def format_repo_names(self, repo):
        repo['repo']['name'] = repo['repo']['name'].replace('/', '_')
        return repo

    def get_context_data(self, *args, **kwargs):
        context = super(ProfilePreview, self).get_context_data(*args, **kwargs)
        context['user'] = User.objects.filter(username=self.request.resolver_match.kwargs['username']).first()
        context['github_oauth_url'] = "https://github.com/login/oauth/authorize?client_id=" + settings.GITHUB_CLIENT_ID + "&scope=repo%2Cuser&state="+self.request.resolver_match.kwargs['username']
        context['authorized_account'] = get_user_info(self.request).json()
        context['projects'] = Project.objects.filter(Q(lead=context['user']) & Q(visibility=Visibility.PUBLIC)).all()
        if context['authorized_account']['message'] != 'Requires authentication':
            context['actions'] = get_user_actions(self.request).json()
            context['actions'] = list(map(lambda x: self.format_repo_names(x), context['actions']))
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
        return context

def starr_project(request, pk=None, username=None):
    if request.method == 'GET':
        project = Project.objects.get(id=pk)
        user = User.objects.get(username=username)
        project.starred.add(user)
        project.save()
        return redirect("../../projects/"+str(project.id))


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
        message = f"New {type_notification} has been made on project {project.title}"
        notification = Notification(project=project, user=user, is_reded=False, message=message)
        notification.save()


def fork_project(request, pk=None, username=None):
    # tj koliko u dublinu da kopiram
    project = Project.objects.filter(id=pk)[0]
    names = project.link.split("/")
    resp = git_fork_projects(request, names[len(names)-2], names[len(names)-1])
    print(resp["html_url"])
    # if 'ref' in resp.keys() and resp['ref'] == "refs/heads/" + new_name:
    #     return redirect('github_branches', username=username, repo=repo)
    # return render(request, "github_create_branch.html",
    #               {'new_name_error': "Renaming was not successful", 'username': username, 'repo': repo})

    #result
    link = resp["html_url"]

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
                              link= resp["html_url"], #novi todo
                              lead = user, fork_parent= project)
        new_project.save()
        saved_project = Project.objects.filter(title=new_project.title, lead = new_project.lead)[0]
        return redirect('../../projects/'+str(saved_project.id))

def changes(request, username, repo, commitsha):
    if username == '_':
        username, repo = repo.split('_') 
    repo_info = get_commit_changes(request, username, repo, commitsha) 
        
    context = {'repo_info': repo_info}

    for f in repo_info["files"]:
        if "patch" in f:
            content = f["patch"].splitlines()
            f["patch"] = copy.deepcopy(content)
    return render(request, 'file_changes.html', context)



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


class PullRequestListView(ListView):
    model = PullRequest
    template_name = 'list_pull_requests.html'
    context_object_name = 'pull_requests'
    ordering = ['id']

    def get_context_data(self, *args, **kwargs):
        context = super(PullRequestListView, self).get_context_data(*args, **kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=context['project_id']).first()
        context['pull_requests'] = PullRequest.objects.filter(project__id=context['project_id'])
        return context

    def get_queryset(self):
        return PullRequest.objects.all()


class PullRequestCreateView(CreateView):
    model = PullRequest
    template_name = 'new_pull_request.html'
    form_class = NewPullRequestForm

    def form_valid(self, form):
        context = self.get_context_data()
        if PullRequest.objects.filter(title=form.instance.title, project=context['project']).exists():
            form.add_error(None, 'Title already in use')
            return super().form_invalid(form)
        form.instance.project = context['project']
        form.instance.creator = self.request.user
        super().form_valid(form)
        Event.save(CreateEvent(task=self.object, author=self.request.user, created_entity_type='Pull request'))
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(PullRequestCreateView, self).get_context_data(**kwargs)
        context['project_id'] = self.request.resolver_match.kwargs['pk']
        context['project'] = Project.objects.filter(id=int(context['project_id'])).first()
        return context

    def get_form_kwargs(self):
        kwargs = super(PullRequestCreateView, self).get_form_kwargs()
        kwargs['project'] = Project.objects.filter(id=int(self.kwargs['pk'])).first()
        return kwargs


class PullRequestUpdateView(UpdateView):
    model = PullRequest
    template_name = 'pull_request_update.html'
    form_class = UpdatePullRequestForm

    def form_valid(self, form):
        context = self.get_context_data()
        if PullRequest.objects.filter(title=form.instance.title, project=context['project']).exists():
            if self.get_object().title != form.instance.title:
                form.add_error(None, 'Title already in use')
                return super().form_invalid(form)


        old_pr = PullRequest.objects.filter(id=form.instance.id).first()
        old_labels = list(old_pr.labels.all()).copy()

        super().form_valid(form)
        
        if(old_labels != list(self.object.labels.all())):
            apply_event = LabelApplication(task=self.object,  author=self.request.user)
            Event.save(apply_event)
            apply_event.applied_labels.set(self.object.labels.all())
            Event.save(apply_event)
            
        diff = find_differences(old_pr, self.object)
        for f in diff:
            Event.save(UpdateEvent(task=self.object, field_name=f[0], old_content=getattr(old_pr, f[0]), new_content=str(f[1]), author=self.request.user))

        if(self.object.labels != old_pr.labels):
            Event.save(LabelApplication(task=self.object, applied_labels=self.object.labels, author=self.request.user))
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super(PullRequestUpdateView, self).get_context_data(**kwargs)
        pull_request = PullRequest.objects.filter(id=int(self.request.resolver_match.kwargs['pk'])).first()
        context['project_id'] = pull_request.project.id
        context['project'] = pull_request.project
        return context

    def get_form_kwargs(self):
        kwargs = super(PullRequestUpdateView, self).get_form_kwargs()
        pull_request = PullRequest.objects.filter(id=int(self.request.resolver_match.kwargs['pk'])).first()
        kwargs['project'] = pull_request.project
        return kwargs


class PullRequestDetailView(DetailView):
    model = PullRequest
    template_name = 'pull_request_detail.html'


def pull_request_new_comment(request, pk):
    reactions = add_reactions()

    pullRequest = PullRequest.objects.filter(id=int(pk)).first()
    if not pullRequest:
        return redirect('/projects')

    form = CommentForm()
    comment_list = Comment.objects.filter(task__id=int(pk))
    comments_reactions = []
    for c in comment_list:
        comments_reactions.append({'comment':c, 'reactions': Reaction.objects.filter(comment=c)})

    events = sorted(chain(CreateEvent.objects.filter(task=pullRequest).all(), UpdateEvent.objects.filter(task=pullRequest).all()\
        , LabelApplication.objects.filter(task=pullRequest).all()), key=lambda instance: instance.date_time)

    obj_dict = {
        'comment_form': form,
        'pr': pullRequest,
        'comments': comments_reactions,
        'reactions': reactions,
        'events' : events
    }

    if request.method == 'POST':
        form_data = CommentForm(request.POST)

        if form_data.is_valid():
            comment = Comment(**form_data.cleaned_data)
            comment.task = pullRequest

            if not request.user.is_authenticated:
                obj_dict['error_add'] = 'User not authenticated'
                return render(request, 'pull_request_detail.html', obj_dict)
            else:
                comment.author = request.user
                comment.date_time = timezone.now()
                comment.save()
                return redirect('/pull/requests/{}'.format(pk))

    return render(request, 'pull_request_detail.html', obj_dict)


class PullRequestDeleteView(DeleteView):
    model = PullRequest
    template_name = 'pull_request_delete.html'

    def get_success_url(self):
        return reverse_lazy('list_pull_requests', kwargs={'pk': self.object.project.id})
        
def list_repositories_auth(request):
    # repo_info = search_repositories_by_user(request, username) # todo request.user.username when connected to github
    repo_info = get_all_visible_repositories_by_user(request)
    account_resp = get_user_info(request)
    # repo_info = get_specific_repository(request, username, "uks")
    if(account_resp.status_code == 200):
        context = {'repo_info': repo_info, 'github_account': account_resp.json()}
        return render(request, 'list_repositories_auth.html', context)
    else:
        return redirect('/user/'+request.user.username, {'user': request.user})


def github_get_specific_repo(request, username, repo):
    repo_info = get_specific_repository(request, username, repo)
    readme = get_specific_repository_readme(request, username, repo)
    readme_content = markdown.markdown(decode_base64_file(readme['content']))

    tree = get_repository_tree(request, username, repo)

    context = {'repo_info': repo_info, 'readme': readme, 'readme_content': readme_content, 'tree': tree}
    return render(request, 'github_get_specific_repo.html', context)


def github_branches(request, username, repo):
    repo_info = get_specific_repository(request, username, repo)
    branches = get_all_branches(request, username, repo)
    context = {'repo_info': repo_info, 'branches': branches, 'username': username,
               'repo': repo}
    return render(request, 'github_branches.html', context)


def github_branch_commits(request, username, repo, branch):
    repo_info = get_specific_repository(request, username, repo)
    if not isinstance(repo_info, list) and 'message' in repo_info.keys() and repo_info['message'] == 'Not Found':
        return page_not_found(request, "There is no repo like that")
    branches = get_all_branches(request, username, repo)
    if branch == 'main':
        commits = get_all_commits_for_branch(request, username, repo, branch)
        if not isinstance(commits, list) and 'message' in commits.keys() and commits['message'] == 'Not Found':
            return redirect('github_branch_commits', username=username, repo=repo, branch='master')
    else:
        commits = get_all_commits_for_branch(request, username, repo, branch)
    context = {'repo_info': repo_info, 'commits': commits, 'branch': branch, 'branches': branches, 'username': username, 'repo': repo}
    return render(request, 'github_branch_commits.html', context)


def github_create_branch(request, username, repo):
    branches = get_all_branches(request, username, repo)
    if request.method == 'GET':
        return render(request, "github_create_branch.html", {'username':username, 'repo':repo, 'branches': branches})
    if request.method == 'POST':
        new_name = request.POST['new_name']
        branch = request.POST['branch']
        for b in branches:
            if new_name == b['name']:
                return render(request, "github_rename_branch.html",
                              {"new_name_error": "Branch with this name already exists", 'username': username,
                               'repo': repo})
        # print(json.loads(branch).commit)
        resp = create_branch(request, username, repo, new_name, branch)
        if 'ref' in resp.keys() and resp['ref'] == "refs/heads/"+new_name:
            return redirect('github_branches', username=username, repo=repo)
        return render(request, "github_create_branch.html", {'new_name_error': "Renaming was not successful", 'username': username, 'repo': repo})


def github_rename_branch(request, username, repo, branch):
    if request.method == 'GET':
        return render(request, "github_rename_branch.html", {'username':username, 'repo':repo, 'branch':branch})
    branches = get_all_branches(request, username, repo)
    if request.method == 'POST':
        new_name = request.POST['new_name']
        for b in branches:
            if new_name == b['name']:
                return render(request, "github_rename_branch.html",
                              {"new_name_error": "Branch with this name already exists", 'username':username, 'repo':repo, 'branch':branch})
        resp = rename_branch(request, username, repo, branch, new_name)
        if 'name' in resp.keys() and resp['name'] == new_name:
            return redirect('github_branches', username=username, repo=repo)
        return render(request, "github_rename_branch.html", {'new_name_error': "Renaming was not successful", 'branch': branch, 'username': username, 'repo': repo})


def github_delete_branch(request, username, repo, branch):
    if request.method == 'GET':
        return render(request, "github_delete_branch.html", {'username':username, 'repo':repo, 'branch':branch})
    if request.method == 'POST':
        resp = delete_branch(request, username, repo, branch)
        if resp.status_code == 204:
            return redirect('github_branches', username=username, repo=repo)
        return render(request, "github_delete_branch.html", {'username': username, 'repo': repo, 'branch': branch, 'err': 'Cannot delete this branch.'})




def after_auth(request):
    """
    This view runs when the user authorizes this app to use all the account and repository info
    """
    
    request_token = request.GET.get('code')
    response = get_access_token(request_token)
    # insert access token into session
    # request.session['access_token'] = response.json()['access_token']
    user = User.objects.get(username=request.GET.get('state'))
    user.access_token = response.json()['access_token']
    user.save()
    return redirect('/login', {})


def insights(request, username, repo):
    project = Project.objects.filter(title=repo, lead__username=username).first()

    context = {
        'repo_owner': username,
        'repo_name': repo,
        'project': project,
        #'project_id': project.id
    }
    return render(request, 'insights.html', context)


def pulse(request, username, repo):
    project = Project.objects.filter(title=repo, lead__username=username).first()
    today = timezone.now()
    date_from = timezone.now() - timedelta(7)
    date_from = date_from
    set_filter = 'hours'
    if request.GET.get('filter'):
        date_filter = request.GET.get('filter')

        if date_filter == 'hours':
            date_from = timezone.now() - timedelta(1)
        elif date_filter == 'days':
            date_from = timezone.now() - timedelta(3)
            set_filter = 'days'

    merged_pull_requests = PullRequest.objects.filter(project=project, state=State.MERGED,
                                                      date_created__range=[date_from, today]).all()
    open_pull_requests = PullRequest.objects.filter(project=project, state=State.OPEN,
                                                    date_created__range=[date_from, today]).all()
    closed_issues = Issue.objects.filter(project=project, is_open=False, date_created__range=[date_from, today]).all()
    new_issues = Issue.objects.filter(project=project, is_open=True,  date_created__range=[date_from, today]).all()

    people_pr_merged = merged_pull_requests.values_list('creator_id', flat=True).distinct()
    people_pr_open = open_pull_requests.values_list('creator_id', flat=True).distinct()
    people_is_closed = closed_issues.values_list('creator_id', flat=True).distinct()
    people_is_new = new_issues.values_list('creator_id', flat=True).distinct()
    context = {
        'filter': set_filter,
        'repo_owner': username,
        'repo_name': repo,
        'date_from': date_from.date(),
        'date_to': today.date(),
        'count_active_pull_requests': len(merged_pull_requests) + len(open_pull_requests),  # 100 / total * x
        'merged_pull_requests': merged_pull_requests,
        'open_pull_requests': open_pull_requests,
        'count_active_issues': len(closed_issues) + len(new_issues),
        'closed_issues': closed_issues,
        'new_issues': new_issues,
        'people_pr_merged': people_pr_merged,
        'people_pr_open': people_pr_open,
        'people_is_closed': people_is_closed,
        'people_is_new': people_is_new

    }

    return render(request, 'pulse.html', context)


def traffic(request, username, repo):
    labels = []
    count = []
    uniques = []
    git_traffic_list = get_repository_traffic(request, username, repo)['clones']
    if len(git_traffic_list) == 0:
        context = {
            'repo_owner': username,
            'repo_name': repo,
        }
        return render(request, 'traffic.html', context)
    start_date = datetime.strptime(git_traffic_list[0]['timestamp'].split('T')[0], '%Y-%m-%d').date()
    end_date = datetime.strptime(git_traffic_list[-1]['timestamp'].split('T')[0], '%Y-%m-%d').date()
    to = [n for n in range(int((end_date - start_date).days))]
    for i in to:
        labels.append(start_date.__str__())
        for item in git_traffic_list:
            if datetime.strptime(item['timestamp'].split('T')[0], '%Y-%m-%d').date() == start_date:
                count.append(item['count'])
                uniques.append(item['uniques'])
                break
            else:
                count.append(0)
                uniques.append(0)

        start_date += timedelta(days=1)

    context = {
        'repo_owner': username,
        'repo_name': repo,
        'labels': labels,
        'count': count,
        'uniques': uniques,
        'result': git_traffic_list
    }

    return render(request, 'traffic.html', context)


def contributors(request, username, repo):
    repo_info = get_specific_repository(request, username, repo)
    if not isinstance(repo_info, list) and 'message' in repo_info.keys() and repo_info['message'] == 'Not Found':
        return page_not_found(request, "There is no repo like that")
    branches = get_all_branches(request, username, repo)
    commits = get_all_commits_for_branch(request, username, repo, 'main')
    if not isinstance(commits, list) and 'message' in commits.keys() and commits['message'] == 'Not Found':
        return
    dates = [n['commit']['author']['date'] for n in commits]
    dates = [datetime.strptime(n.split('T')[0], '%Y-%m-%d').date() for n in dates]

    start_date = dates[-1]
    end_date = timezone.now().date()
    to = [n for n in range(int((end_date - start_date).days))]

    labels = []
    counts = []
    # { 'developer' : { 'date': x, 'counts': y } }
    developer_map = {}
    for i in to:
        labels.append(str(start_date))
        count = 0
        for item in commits:
            if datetime.strptime(item['commit']['author']['date'].split('T')[0], '%Y-%m-%d').date() == start_date:
                count += 1
                author = item['commit']['author']['name']
                if author in developer_map:
                    if start_date in developer_map[author]:
                        developer_map[author][start_date] += 1
                    else:
                        developer_map[author][start_date] = 0
                else:
                    developer_map[author] = {}
                    developer_map[author][start_date] = 0

        counts.append(count)
        developers = developer_map.keys()
        for developer in developers:
            if start_date in developer_map[developer]:
                continue
            else:
                developer_map[developer][start_date] = 0

        start_date += timedelta(days=1)

    for developer in developer_map.keys():
        developer_map[developer] = list(developer_map[developer].values())
    context = {
        'repo_info': repo_info,
        'commits': commits,
        'branches': branches,
        'repo_owner': username,
        'repo_name': repo,
        'dates': dates,
        'labels': labels,
        'counts': counts,
        'developer_map': developer_map
    }

    return render(request, 'contributors.html', context)


def commits_chart(request, username, repo):
    repo_info = get_specific_repository(request, username, repo)
    if not isinstance(repo_info, list) and 'message' in repo_info.keys() and repo_info['message'] == 'Not Found':
        return page_not_found(request, "There is no repo like that")
    branches = get_all_branches(request, username, repo)
    commits = get_all_commits_for_branch(request, username, repo, 'main')
    if not isinstance(commits, list) and 'message' in commits.keys() and commits['message'] == 'Not Found':
        return
    dates = [n['commit']['author']['date'] for n in commits]
    dates = [datetime.strptime(n.split('T')[0], '%Y-%m-%d').date() for n in dates]

    start_date = dates[-1]
    end_date = timezone.now().date()
    to = [n for n in range(int((end_date - start_date).days))]

    labels = []
    counts = []

    for i in to:
        labels.append(str(start_date))
        count = 0
        for item in commits:
            if datetime.strptime(item['commit']['author']['date'].split('T')[0], '%Y-%m-%d').date() == start_date:
                count += 1
        counts.append(count)

        start_date += timedelta(days=1)

    context = {
        'repo_info': repo_info,
        'commits': commits,
        'branches': branches,
        'repo_owner': username,
        'repo_name': repo,
        'labels': labels,
        'counts': counts,
    }

    return render(request, 'commits.html', context)


def forks(request, username, repo):
    forks_info = get_forks(request, username, repo)
    # { 'user' : 'repo' }
    forks_map = {}
    for fork in forks_info:
        forks_map[fork['full_name']] = fork['html_url']

    context = {
        'repo_owner': username,
        'repo_name': repo,
        'forks': forks_map,
    }

    return render(request, 'forks.html', context)


def code_frequency(request, username, repo):
    git_code_frequency = get_code_frequency(request, username, repo)
    temp_date = [datetime.fromtimestamp(n[0]).date() for n in git_code_frequency]

    labels = []
    added = []
    deleted = []

    if len(git_code_frequency) == 0:
        context = {
            'repo_owner': username,
            'repo_name': repo,
        }
        return render(request, 'code_frequency.html', context)

    start_date = temp_date[0]
    end_date = temp_date[-1]
    to = [n for n in range(int((end_date - start_date).days))]
    for i in to:
        labels.append(start_date.__str__())
        add_count = 0
        delete_count = 0
        for item in git_code_frequency:
            if datetime.fromtimestamp(item[0]).date() == start_date:
                add_count += item[1]
                delete_count += item[2]

        added.append(add_count)
        deleted.append(delete_count)
        start_date += timedelta(days=1)

    context = {
        'repo_owner': username,
        'repo_name': repo,
        'labels': labels,
        'added': added,
        'deleted': deleted
    }

    return render(request, 'code_frequency.html', context)


def advanced_search(request, project_id, user_id):
    if request.method == 'GET':
        return render(request, "advanced_search_result.html",
                      {'project_id': project_id, 'user_id': user_id, 'selected': 2})
    if request.method == 'POST':
        obj_dict = {
            'keyword': request.POST['keyword'],
            'project_id': project_id,
            'user_id': user_id,
            'selected': 2
        }
        if 'search_user' in request.POST:
            obj_dict['search_type'] = 's2'
            u = User.objects.filter(id=user_id).first()
            if 'user:' not in obj_dict['keyword']:
                obj_dict['keyword'] = request.POST['keyword'] + " user:" + u.username + " author:" + u.username
        if 'search_all' in request.POST:
            obj_dict['search_type'] = 's1'
        if 'search_project' in request.POST:
            obj_dict['search_type'] = 's3'

        if obj_dict['keyword'] not in {None, ''}:
             #return render(request, "advanced_search_result.html", obj_dict)
            return redirect('advanced_search_results', project_id=project_id,
                            user_id=user_id, keyword=obj_dict['keyword'],
                            search_type=obj_dict['search_type'], selected=obj_dict['selected'])

        return render(request, "advanced_search.html", {'new_name_error': "Seaarch was not successful"})


def toggle_search_results(request, project_id, user_id, keyword, search_type, selected):
    if request.method == 'GET':
        return redirect('advanced_search_results', project_id=project_id,
                        user_id=user_id, keyword=keyword, search_type=search_type, selected=selected)


def advanced_search_result(request, project_id, user_id, keyword=None,  search_type=None, selected=2):
    obj_dict = {
        'project_id': project_id,
        'user_id': user_id,
        'keyword': keyword,
        'selected': selected,
        'iss': 'issue'
    }
    if 's2' in search_type:
        obj_dict['search_type'] = 's2'
        u = User.objects.filter(id=user_id).first()
        obj_dict['info'] = u.username
        if 'user:' not in obj_dict['keyword']:
            obj_dict['keyword'] = keyword + " user:" + u.username + " author:" + u.username
        obj_dict['projects'], obj_dict['issues'], obj_dict['prs'] = search_in_user(obj_dict['keyword'], request.user)
    if 's1' in search_type:
        obj_dict['search_type'] = 's1'
        obj_dict['projects'], obj_dict['issues'], obj_dict['users'], obj_dict['prs'] = search_in_github(obj_dict['keyword'], request.user)
    if 's3' in search_type:
        obj_dict['search_type'] = 's3'
        p = Project.objects.filter(id=project_id).first()
        obj_dict['info'] = p.title
        obj_dict['issues'], obj_dict['prs'] = search_in_project(obj_dict['keyword'], request.user, project_id)
    if obj_dict['keyword'] not in {None, ''}:
        return render(request, "advanced_search_result.html", obj_dict)
    return render(request, "advanced_search_result.html", {'new_name_error': "Seaarch was not successful"})


def tasks_filter(request, task_type, selected_tab):
    if request.method == 'GET':
        obj_dict = {
            'task_type': task_type,
            'selected_tab': selected_tab,
            'query': '',
        }
        if task_type in ['pr', 'issue']:
            if selected_tab == 1: #created
                obj_dict['query'] = "is:" + task_type + " author:"+request.user.username
            elif selected_tab == 2: #assigned
                obj_dict['query'] = "is:" + task_type + " assignee:" + request.user.username
            else:
                obj_dict['query'] = "is:" + task_type
        else:
            if selected_tab == 1: #created
                obj_dict['query'] = "author:"+request.user.username
            elif selected_tab == 2: #assigned
                obj_dict['query'] = "assignee:" + request.user.username
            else:
                obj_dict['query'] = ""

        obj_dict['tasks'] = filter_query(obj_dict['query'], request.user)
        return render(request, "tasks_filter.html", obj_dict)

    if request.method == 'POST':
        obj_dict = {
            'query': request.POST['query'],
            'selected_tab': selected_tab,
            'task_type': task_type,
        }
        if obj_dict['query'] not in {None, ''}:
            obj_dict['tasks'] = filter_query(obj_dict['query'], request.user)
            return render(request, "tasks_filter.html", obj_dict)
        return render(request, "tasks_filter.html", {'new_name_error': "Filter was not successful"})


def forward_to_view_task(request, pk):
    if Issue.objects.filter(id=pk):
        return redirect('issue_detail', pk=pk)
    else:
        return redirect('pull_request_detail', pk=pk)

from django.apps.registry import apps
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)
from .models import Project, User, Milestone


def index(request):
    title = apps.get_app_config('mini_githubcic').verbose_name
    return render(request, 'index.html', {"title": title})


def login(request, id=None):
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

            return render(request, "index.html", {"title": "first page"})

        except:
            return render(request, "login.html",
                          {"users_error": "User with this username and password does not exist"})

class ProjectListView(ListView):
    model = Project
    template_name = 'list_projects.html'
    context_object_name = 'projects'
    ordering = ['title']

    def get_queryset(self):
        return Project.objects.all()


class ProjectCreateView(CreateView):
    model = Project
    template_name = 'new_project.html'
    fields = ['title', 'description', 'licence', 'visibility']

    def form_valid(self, form):
        # TODO link to logged in user
        form.instance.lead = User.objects.get(username="U1")
        form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
        if Project.objects.filter(title=form.instance.title).exists():
            form.add_error('titleExists', 'Title already in use')#ovde imam gresku??

        return super().form_valid(form)


class ProjectUpdateView(UpdateView):
    model = Project
    template_name = 'project_update.html'
    fields = ['title', 'description']

    def form_valid(self, form):

        if Project.objects.filter(title=form.instance.title).exists():#ovde kopirati kao kod mene jer izaziva gresku
            if self.get_object().name != form.instance.name:
                form.add_error('titleExists', 'Title already in use')#ovde imam gresku??

        return super().form_valid(form)


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'


class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'project_delete.html'
    success_url = '/projects'

    def test_func(self):
        # TODO check if request sender is project lead
        return True

class MilestoneListView(ListView):
    # TODO per project
    model = Milestone
    template_name = 'list_milestones.html'
    context_object_name = 'milestones'
    ordering = ['title']

    def get_queryset(self):
        return Milestone.objects.all()

class MilestoneCreateView(CreateView):
    model = Milestone
    template_name = 'new_milestone.html'
    fields = ['title', 'description',  'state']#'due_date',

    def form_valid(self, form):
        # TODO link to logged in user
        # TODO project
        form.instance.lead = User.objects.get(username="U1")
        form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
        if Milestone.objects.filter(title=form.instance.title).exists():
            form.add_error('titleExists', 'Title already in use') #ovde imam gresku??

        return super().form_valid(form)

class MilestoneUpdateView(UpdateView):
    model = Milestone
    template_name = 'milestone_update.html'
    fields = ['title', 'description',  'state']#'due_date',

    def form_valid(self, form):

        print(Milestone.objects.filter(title=form.instance.title))
        if len(Milestone.objects.filter(title=form.instance.title)) != 0: #pazi da je na nivou projekta TODO
            if self.get_object().title != form.instance.title:
                form.add_error('titleExists', 'Title already in use') #ovde imam gresku??

        return super().form_valid(form)


class MilestoneDetailView(DetailView):
    model = Milestone
    template_name = 'milestone_detail.html'


class MilestoneDeleteView(DeleteView):
    model = Milestone
    template_name = 'milestone_delete.html'
    success_url = '/milestones'

    def test_func(self):
        # TODO check if request sender is project lead
        return True

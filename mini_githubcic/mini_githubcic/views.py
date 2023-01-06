from django.apps.registry import apps
from django.shortcuts import render
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView
)
from .models import  User

def index(request):
    title = apps.get_app_config('mini_githubcic').verbose_name
    return render(request,'index.html',{"title":title})

def login(request,id=None):
    #title = apps.get_app_config('login').verbose_name
    if request.method == 'GET':
        return render(request, "login.html")
    if request.method=='POST':
        users=User.objects.all()

        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username=username)
        if user is None:
            return render(request, "login.html",
                         { "users_error": "User with this username and password does not exist"}) #"title": title,

        if user.password != password:
            return render(request, "login.html",
                          { "users_error": "User with this username and password does not exist"}) #,"title": title,

        else:
            return render(request, "index.html", {"title": "first page"})

# class LoginView(CreateView):
#     model = Project
#     template_name = 'login.html'
#     context_object_name = 'login'
#     ordering = ['title']
#
#     def form_valid(self, form):
#         # TODO link to logged in user
#         form.instance.lead = User.objects.get(username="U1")
#         form.instance.link = "https://github.com/" + form.instance.lead.username + "/" + form.instance.title + ".git"
#         if Project.objects.filter(title=form.instance.title).exists():
#             form.add_error('titleExists', 'Title already in use')
#
#         return super().form_valid(form)

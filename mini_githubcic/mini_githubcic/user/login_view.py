from django.apps.registry import apps
from django.shortcuts import render

from ..models import  User


def login(request,id=None):
    title = apps.get_app_config('login').verbose_name
    if request.method=='POST':
        users=User.objects.all()

        username = request.POST['username']
        password = request.POST['password']
        user = User.objects.get(username=username)
        if user is None:
            return render(request, "login.html",
                         { "title": title,"users_error": "User with this username and password does not exist"}) #

        if user.password != password:
            return render(request, "login.html",
                          {"title": title, "users_error": "User with this username and password does not exist"}) #,

        else:
            return render(request, "first_page.html", {"title": "first page"})
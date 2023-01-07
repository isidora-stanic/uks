"""mini_githubcic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('projects/', ProjectListView.as_view(), name='list_projects'),
    path('projects/add', ProjectCreateView.as_view(), name='add_project'),
    path('projects/<int:pk>', ProjectDetailView.as_view(), name='project_detail'),
    path('projects/<int:pk>/update', ProjectUpdateView.as_view(), name='project_update'),
    path('projects/<int:pk>/delete', ProjectDeleteView.as_view(), name='project_delete'),
    path('milestones/', MilestoneListView.as_view(), name='list_milestones'),
    path('milestones/add', MilestoneCreateView.as_view(), name='add_milestone'),
    path('milestones/<int:pk>', MilestoneDetailView.as_view(), name='milestone_detail'),
    path('milestones/<int:pk>/update', MilestoneUpdateView.as_view(), name='milestone_update'),
    path('milestones/<int:pk>/delete', MilestoneDeleteView.as_view(), name='milestone_delete')
]

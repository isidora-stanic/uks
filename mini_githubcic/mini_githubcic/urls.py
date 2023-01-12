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
    path('projects/<int:pk>/milestones/', MilestoneListView.as_view(), name='list_milestones'),
    path('projects/<int:pk>/milestones/add', MilestoneCreateView.as_view(), name='add_milestone'),
    path('milestones/<int:pk>', MilestoneDetailView.as_view(), name='milestone_detail'),
    path('milestones/<int:pk>/update', MilestoneUpdateView.as_view(), name='milestone_update'),
    path('milestones/<int:pk>/delete', MilestoneDeleteView.as_view(), name='milestone_delete'),
    path('projects/<int:pk>/issues/', IssueListView.as_view(), name='project_issues'),
    path('projects/<int:pk>/issues/add', IssueCreateView.as_view(), name='add_issue'),
    path('issues/<int:pk>', IssueDetailView.as_view(), name='issue_detail'),
    path('issues/<int:pk>/update', IssueUpdateView.as_view(), name='issue_update'),
    path('issues/<int:pk>/delete', IssueDeleteView.as_view(), name='issue_delete'),
    path('issues/<int:pk>/state-toggle', issue_state_toggle, name='issue_state_toggle'),
    path('milestones/<int:pk>/close', milestone_close, name='milestone_close'),
    path('projects/<int:pk>/labels', LabelListView.as_view(), name='list_labels'),
    path('projects/<int:pk>/labels/add', LabelCreateView.as_view(), name='add_label'),
    path('labels/<int:pk>', LabelDetailView.as_view(), name='label_detail'),
    path('labels/<int:pk>/update', LabelUpdateView.as_view(), name='label_update'),
    path('labels/<int:pk>/delete', LabelDeleteView.as_view(), name='label_delete'),
    path('starredProjects/<int:pk>', StarredProjectListView.as_view(), name='list_starred_projects'),
    path('starProject/<int:pk>', starr_project, name='star_project'),
    path('unstarProject/<int:pk>', unstarr_project, name='unstar_project'),
    path('watchedProjects/<int:pk>', WatchedProjectListView.as_view(), name='list_watched_projects'),
    path('watchProject/<int:pk>', watch_project, name='watch_project'),
    path('unwatchProject/<int:pk>', unwatch_project, name='unwatch_project')
]

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
from django.urls import include, path
from .views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),

    path('login/', sign_in, name='login'),
    path('logout/', sign_out, name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('user/<slug:username>', ProfilePreview.as_view(), name='profile_preview'),
    path('login/oauth2/code/github', after_auth, name='after_auth'),

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
    path('milestones/<int:pk>/close', milestone_close, name='milestone_close'),

    path('projects/<int:pk>/issues/', IssueListView.as_view(), name='project_issues'),
    path('projects/<int:pk>/issues/add', IssueCreateView.as_view(), name='add_issue'),
    path('issues/<int:pk>', new_comment, name='issue_detail'),
    path('issues/<int:pk>/update', IssueUpdateView.as_view(), name='issue_update'),
    path('issues/<int:pk>/delete', IssueDeleteView.as_view(), name='issue_delete'),
    path('issues/<int:pk>/state-toggle', issue_state_toggle, name='issue_state_toggle'),

    path('projects/<int:pk>/labels', LabelListView.as_view(), name='list_labels'),
    path('projects/<int:pk>/labels/add', LabelCreateView.as_view(), name='add_label'),
    path('labels/<int:pk>', LabelDetailView.as_view(), name='label_detail'),
    path('labels/<int:pk>/update', LabelUpdateView.as_view(), name='label_update'),
    path('labels/<int:pk>/delete', LabelDeleteView.as_view(), name='label_delete'),

    path('starred-projects/<slug:username>', StarredProjectListView.as_view(), name='list_starred_projects'),
    path('star-project/<int:pk>/<slug:username>', starr_project, name='star_project'),
    path('unstar-project/<int:pk>/<slug:username>', unstarr_project, name='unstar_project'),
    path('watched-projects/<slug:username>', WatchedProjectListView.as_view(), name='list_watched_projects'),
    path('watch-project/<int:pk>/<slug:username>', watch_project, name='watch_project'),
    path('unwatch-project/<int:pk>/<slug:username>', unwatch_project, name='unwatch_project'),
    path('my-notifications/<slug:username>', MyNotificationsListView.as_view(), name='list_notifications'),
    path('fork-project/<int:pk>/<slug:username>', fork_project, name='fork_project'),

    path('changes/<slug:username>/<slug:repo>/<slug:commitsha>', changes, name='changes'),

    # path('projects/<int:pk>/branches/', BranchListView.as_view(), name='project_branches'),
    # path('projects/<int:pk>/branches/add', new_branch, name='add_branch'),
    # path('branches/<int:pk>', BranchDetailView.as_view(), name='branch_detail'),
    # path('branches/<int:pk>/update', BranchUpdateView.as_view(), name='branch_update'),
    # path('branches/<int:pk>/delete', BranchDeleteView.as_view(), name='branch_delete'),
    # path('branches/<int:pk>/commits/add', CommitCreateView.as_view(), name='add_commit'),
    # path('commits/<int:pk>', CommitDetailView.as_view(), name='commit_detail'),

    path('comments/<int:pk>/update', CommentUpdateView.as_view(), name='comment_update'),
    path('comments/<int:pk>/delete', CommentDeleteView.as_view(), name='comment_delete'),
    path('comments/<int:pk>/reaction/<str:rid>', toggle_reaction, name='comment_reaction'),

    path('projects/<int:pk>/pull/requests/', PullRequestListView.as_view(), name='list_pull_requests'),
    path('projects/<int:pk>/pull/requests/add', PullRequestCreateView.as_view(), name='add_pull_request'),
    path('pull/requests/<int:pk>', pull_request_new_comment, name='pull_request_detail'),
    path('pull/requests/<int:pk>/update', PullRequestUpdateView.as_view(), name='pull_request_update'),
    path('pull/requests/<int:pk>/delete', PullRequestDeleteView.as_view(), name='pull_request_delete'),

    path('github_repos', list_repositories_auth, name='list_repo_auth'),
    path('github_repos/<slug:username>/<slug:repo>/branches', github_branches, name='github_branches'),
    path('github_repos/<slug:username>/<slug:repo>/<str:branch>/commits', github_branch_commits, name='github_branch_commits'),
    path('github_repos/<slug:username>/<slug:repo>/branches/create', github_create_branch, name='github_create_branch'),
    path('github_repos/<slug:username>/<slug:repo>/branches/<str:branch>/rename', github_rename_branch, name='github_rename_branch'),
    path('github_repos/<slug:username>/<slug:repo>/branches/<str:branch>/delete', github_delete_branch, name='github_delete_branch'),

]

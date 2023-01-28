from .models import *


def find_differences(old_obj, updated_obj):
    old_values = [(k,v) for k,v in old_obj.__dict__.items() if k != '_state']
    new_values = [(k,v) for k,v in updated_obj.__dict__.items() if k != '_state']
    diff = [f for f in new_values if f not in old_values]
    return diff


def search_in_project(keyword, project_id):
    issue_list = Issue.objects.filter(project__id=project_id)
    pr_list = PullRequest.objects.filter(project__id=project_id)
    if " " in keyword:
        klist = keyword.split(" ")
        filtered_issues = [x for x in issue_list for k in klist
                       if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                       any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower())]
        filtered_prs = [x for x in pr_list for k in klist
                           if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower())]
        return filtered_issues, filtered_prs
    else:
        filtered_issues = [x for x in issue_list
                       if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                       any(y for y in Comment.objects.filter(task__id=x.id) if keyword.lower() in y.content.lower())]
        filtered_prs = [x for x in pr_list
                           if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]
        return filtered_issues, filtered_prs


def search_in_user(keyword, user_id):
    project_list = Project.objects.filter(lead__id=user_id)
    issue_list = Issue.objects.filter(project__lead__id=user_id)
    pr_list = PullRequest.objects.filter(project__lead__id=user_id)
    if " " in keyword:
        klist = keyword.split(" ")
        filtered_projects = [p for p in project_list if
                             any(k for k in klist if k.lower() in p.title.lower()
                                 or k.lower() in p.description.lower() or
                                 any(x for x in Issue.objects.filter(project__id=p.id)
                                     if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                                     any(y for y in Comment.objects.filter(task__id=x.id) if
                                                                    k.lower() in y.content.lower())) or
                                 any(x for x in PullRequest.objects.filter(project__id=p.id)
                                     if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                                     any(y for y in Comment.objects.filter(task__id=x.id) if
                                         k.lower() in y.content.lower()))
                                 )]
        filtered_issues = [x for x in issue_list if any(k for k in klist
                           if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower()))]

        filtered_prs = [x for x in pr_list if any(k for k in klist
                           if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower()))]
        return filtered_projects, filtered_issues, filtered_prs
    else:
        filtered_projects = [p for p in project_list
                             if keyword.lower() in p.title.lower() or keyword.lower() in p.description.lower() or
                             any(x for x in Issue.objects.filter(project__id=p.id)
                                 if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                                 any(y for y in Comment.objects.filter(task__id=x.id) if
                                     keyword.lower() in y.content.lower())) or
                             any(x for x in PullRequest.objects.filter(project__id=p.id)
                                 if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                                 any(y for y in Comment.objects.filter(task__id=x.id) if
                                     keyword.lower() in y.content.lower()))
                             ]
        filtered_issues = [x for x in issue_list
                           if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]

        filtered_prs = [x for x in pr_list
                           if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]
        return filtered_projects, filtered_issues, filtered_prs


def search_in_github(keyword):
    issue_list = Issue.objects.all()
    project_list = Project.objects.all()
    user_list = User.objects.all()
    pr_list = PullRequest.objects.all()
    if " " in keyword:
        klist = keyword.split(" ")
        filtered_issues = [x for x in issue_list if any(k for k in klist
                       if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                       any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower()))]

        filtered_projects = [p for p in project_list if any(k for k in klist
                            if k.lower() in p.title.lower() or k.lower() in p.description.lower() or
                            any(x for x in Issue.objects.filter(project__id=p.id)
                            if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                            any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower())) or
                            any(x for x in PullRequest.objects.filter(project__id=p.id)
                            if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                            any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower())))]

        filtered_users = [u for u in user_list if any(k for k in klist if k.lower() in u.username.lower())]
        filtered_prs = [x for x in pr_list if
                        any(k for k in klist if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                            any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower()))]
        return filtered_projects, filtered_issues, filtered_users, filtered_prs
    else:
        filtered_issues = [x for x in issue_list
                       if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                       any(y for y in Comment.objects.filter(task__id=x.id) if keyword.lower() in y.content.lower())]

        filtered_projects = [p for p in project_list
                             if keyword.lower() in p.title.lower() or keyword.lower() in p.description.lower() or
                             any(x for x in Issue.objects.filter(project__id=p.id)
                             if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                             any(y for y in Comment.objects.filter(task__id=x.id) if
                            keyword.lower() in y.content.lower())) or
                             any(x for x in PullRequest.objects.filter(project__id=p.id)
                                 if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                                 any(y for y in Comment.objects.filter(task__id=x.id) if
                                     keyword.lower() in y.content.lower()))
                             ]

        filtered_users = [u for u in user_list if keyword.lower() in u.username.lower()]
        filtered_prs = [x for x in pr_list
                           if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]
        return filtered_projects, filtered_issues, filtered_users, filtered_prs
from .models import *
from itertools import chain


def find_differences(old_obj, updated_obj):
    old_values = [(k, v) for k, v in old_obj.__dict__.items() if k != '_state']
    new_values = [(k, v) for k, v in updated_obj.__dict__.items() if k != '_state']
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
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]
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
                                 or k.lower() in p.description.lower()
                                 )]
        filtered_issues = [x for x in issue_list if any(k for k in klist
                                                        if
                                                        k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                                                        any(y for y in Comment.objects.filter(task__id=x.id) if
                                                            k.lower() in y.content.lower()))]

        filtered_prs = [x for x in pr_list if any(k for k in klist
                                                  if
                                                  k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                                                  any(y for y in Comment.objects.filter(task__id=x.id) if
                                                      k.lower() in y.content.lower()))]
        return filtered_projects, filtered_issues, filtered_prs
    else:
        filtered_projects = [p for p in project_list
                             if keyword.lower() in p.title.lower() or keyword.lower() in p.description.lower()
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
                                                        if
                                                        k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                                                        any(y for y in Comment.objects.filter(task__id=x.id) if
                                                            k.lower() in y.content.lower()))]

        filtered_projects = [p for p in project_list if any(k for k in klist
                                                            if
                                                            k.lower() in p.title.lower() or k.lower() in p.description.lower())]

        filtered_users = [u for u in user_list if any(k for k in klist if k.lower() in u.username.lower())]
        filtered_prs = [x for x in pr_list if
                        any(k for k in klist if k.lower() in x.title.lower() or k.lower() in x.description.lower() or
                            any(y for y in Comment.objects.filter(task__id=x.id) if k.lower() in y.content.lower()))]
        return filtered_projects, filtered_issues, filtered_users, filtered_prs
    else:
        filtered_issues = [x for x in issue_list
                           if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                           any(y for y in Comment.objects.filter(task__id=x.id) if
                               keyword.lower() in y.content.lower())]

        filtered_projects = [p for p in project_list
                             if keyword.lower() in p.title.lower() or keyword.lower() in p.description.lower()]

        filtered_prs = [x for x in pr_list
                        if keyword.lower() in x.title.lower() or keyword.lower() in x.description.lower() or
                        any(y for y in Comment.objects.filter(task__id=x.id) if
                            keyword.lower() in y.content.lower())]

        filtered_users = [u for u in user_list if keyword.lower() in u.username.lower()]

        return filtered_projects, filtered_issues, filtered_users, filtered_prs


def filter_query(query):
    tasks = []
    priority = ''
    if 'is:pr' in query and 'is:issue' in query:
        i1 = query.find('is:pr')
        i2 = query.find('is:issue')
        priority = ['pr' if i1 < i2 else 'issue']

    if 'is:pr' in query and ((priority is '') or ('is:issue' in query and priority is 'pr')):
        tasks = filter_query_prs(query)
    elif 'is:issue' in query and ((priority is '') or ('is:pr' in query and priority is 'issue')):
        tasks = filter_query_issues(query)
    else:
        tasks = set(chain(set(filter_query_prs(query)), set(filter_query_issues(query))))

    return tasks


def filter_query_issues(query):
    tasks = Issue.objects.all()
    if 'is:open' in query:
        tasks = tasks.filter(is_open=True)
    if 'is:closed' in query:
        tasks = tasks.filter(is_open=False)
    if 'author:' in query:
        i = query.find('author:')
        author = query[i + 7:].split(" ")[0]
        tasks = tasks.filter(creator__username=author)
    if 'assignee:' in query:
        i = query.find('assignee:')
        assignee = query[i + 9:].split(" ")[0]
        tasks = tasks.filter(assigned_to__username=assignee)
    if 'no:assignee' in query:
        tasks = tasks.filter(assigned_to=None)
    return tasks


def filter_query_prs(query):
    tasks = PullRequest.objects.all()
    if 'is:open' in query:
        tasks = tasks.filter(state='OPEN')
    if 'is:closed' in query:
        tasks = tasks.filter(state='CLOSED')
    if 'author:' in query:
        i = query.find('author:')
        author = query[i + 7:].split(" ")[0]
        tasks = tasks.filter(creator__username=author)
    if 'assignee:' in query:
        i = query.find('assignee:')
        assignee = query[i + 9:].split(" ")[0]
        tasks = tasks.filter(assigned_to__username=assignee)
    if 'no:assignee' in query:
        tasks = tasks.filter(assigned_to=None)
    return tasks

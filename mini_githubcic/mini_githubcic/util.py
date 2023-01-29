from .models import *
from itertools import chain
from django.db.models import Q


def find_differences(old_obj, updated_obj):
    old_values = [(k, v) for k, v in old_obj.__dict__.items() if k != '_state']
    new_values = [(k, v) for k, v in updated_obj.__dict__.items() if k != '_state']
    diff = [f for f in new_values if f not in old_values]
    return diff


def search_in_project(keyword, user):
    filtered_issues = list(filter_query_issues(keyword, user))
    filtered_prs = list(filter_query_prs(keyword, user))
    return filtered_issues, filtered_prs


def search_in_user(keyword, user):
    filtered_projects = list(search_query_projects(keyword, user))
    filtered_issues = list(filter_query_issues(keyword, user))
    filtered_prs = list(filter_query_prs(keyword, user))
    return filtered_projects, filtered_issues, filtered_prs


def search_in_github(keyword, user):
    filtered_projects = list(search_query_projects(keyword, user))
    filtered_issues = list(filter_query_issues(keyword, user))
    filtered_prs = list(filter_query_prs(keyword, user))
    filtered_users = list(search_query_users(keyword))
    return filtered_projects, filtered_issues, filtered_users, filtered_prs


def search_query_users(query):
    users = User.objects.all()
    options = query.split(" ")
    word = [x for x in options if x.find(":") == -1]
    if len(word) >= 1:
        for w in word:
            users = users.filter(username__contains=w.lower())
    return users


def search_query_projects(query, user):
    projects = Project.objects.all()
    options = query.split(" ")
    word = [x for x in options if x.find(":") == -1]
    if 'is:public' in query:
        projects = projects.filter(visibility='PUBLIC')
    if 'is:private' in query:
        projects = projects.filter(Q(visibility=Visibility.PRIVATE) &
                         (Q(lead__id=user.id) | Q(developers=user))).distinct()
    if 'is:public' not in query and 'is:private' not in query:
        projects = projects.filter(Q(visibility=Visibility.PUBLIC) | (Q(visibility=Visibility.PRIVATE) &
                            (Q(lead__id=user.id) | Q( developers=user)))).distinct()
    if 'in:name' in query:
        projects = projects.filter(Q(title__contains=word[0].lower())).distinct()
    if 'in:description' in query:
        projects = projects.filter(Q(description__contains=word[0].lower())).distinct()
    if 'in:name,description' in query:
        projects = projects.filter(title__contains=word[0].lower(), description__contains=word[0].lower()).distinct()
    if ('in:name' and 'in:name,description' and 'in:description') not in query :
        projects = projects.filter(title__contains=word[0].lower(), description__contains=word[0].lower()).distinct()
    if 'user:' in query:
        i = query.find('user:')
        author = query[i + 5:].split(" ")[0]
        projects = projects.filter(lead__username__contains=author.lower())
    if 'repo:' in query:
        i = query.find('repo:')
        params = (query[i + 5:].split(" ")[0]).split('/')
        projects = projects.filter(lead__username__contains=params[0].lower(),title__contains=params[1].lower())
    if 'forks:' in query:
        i = query.find('forks:')
        params = query[i + 6:].split(" ")[0]
        if ('>' and '<' and '>=' and '<=' and '..') not in params:
            val = params[1:]
            projects = projects.filter(number_of_forked_project=val).distinct()
        if '>' in params:
            val = params[1:]
            projects = projects.filter(number_of_forked_project__gt=val).distinct()
        if '>=' in params:
            val = params[1:]
            projects = projects.filter(number_of_forked_project__gte=val).distinct()
        if '<' in params:
            val = params[1:]
            projects = projects.filter(number_of_forked_project__lt=val).distinct()
        if '<=' in params:
            val = params[1:]
            projects = projects.filter(number_of_forked_project__lte=val).distinct()
        if '..' in params:
            vals = params.split("..")
            projects = projects.filter(number_of_forked_project__lt=vals[1], number_of_forked_project__gt=vals[0]).distinct()

    return projects


def filter_query(query, user):
    priority = ''
    if 'is:pr' in query and 'is:issue' in query:
        i1 = query.find('is:pr')
        i2 = query.find('is:issue')
        priority = ['pr' if i1 < i2 else 'issue']

    if 'is:pr' in query and ((priority is '') or ('is:issue' in query and priority is 'pr')):
        # tasks = filter_query_prs(query, user)
        f1_keys = [x.id for x in filter_query_prs(query, user)]
        tasks = PullRequest.objects.filter(id__in=f1_keys)
        return tasks
    elif 'is:issue' in query and ((priority is '') or ('is:pr' in query and priority is 'issue')):
        # tasks = filter_query_issues(query, user)
        f2_keys = [x.id for x in filter_query_issues(query, user)]
        tasks = Issue.objects.filter(id__in=f2_keys)
        return tasks
    else:
        # tasks = set(chain(set(filter_query_prs(query, user)), set(filter_query_issues(query, user))))
        f1_keys = [x.id for x in filter_query_prs(query, user)]
        f2_keys = [x.id for x in filter_query_issues(query, user)]
        tasks = set(chain(PullRequest.objects.filter(id__in=f1_keys), Issue.objects.filter(id__in=f2_keys)))
        return tasks


def filter_query_issues(query, user):
    tasks = Issue.objects.all()
    if 'is:open' in query or 'state:open' in query:
        tasks = tasks.filter(is_open=True)
    if 'is:closed' in query or 'state:closed' in query:
        tasks = tasks.filter(is_open=False)

    tasks = filter_params(query, tasks, user)
    return tasks


def filter_query_prs(query, user):
    tasks = PullRequest.objects.all()
    if 'is:open' in query or 'state:open' in query:
        tasks = tasks.filter(state='OPEN')
    if 'is:closed' in query or 'state:closed' in query:
        tasks = tasks.filter(state='CLOSED')

    tasks = filter_params(query, tasks, user)
    return tasks


def filter_params(query, tasks, user):
    filters = query.split(" ")
    word = [x for x in filters if x.find(":") == -1]
    if 'is:public' in query:
        tasks = tasks.filter(project__visibility='PUBLIC')
    if 'is:private' in query:
        t = tasks.filter(Q(project__visibility=Visibility.PRIVATE) &
                         (Q(project__lead__id=user.id) | Q(project__developers=user))).distinct()
        tasks = t
    if 'is:public' not in query and 'is:private' not in query:
        t = tasks.filter(Q(project__visibility=Visibility.PUBLIC) | (Q(project__visibility=Visibility.PRIVATE) &
                                                                     (Q(project__lead__id=user.id) | Q(
                                                                         project__developers=user)))).distinct()
        tasks = t
    if ('-author:' not in query) and 'author:' in query:
        i = query.find('author:')
        author = query[i + 7:].split(" ")[0]
        tasks = tasks.filter(creator__username__contains=author.lower())
    if '-author:' in query:
        i = query.find('-author:')
        author = query[i + 8:].split(" ")[0]
        tasks = tasks.exclude(creator__username__contains=author.lower())
    if 'assignee:' in query:
        i = query.find('assignee:')
        assignee = query[i + 9:].split(" ")[0]
        tasks = tasks.filter(assigned_to__username__contains=assignee.lower())
    if 'no:assignee' in query:
        tasks = tasks.filter(assigned_to=None)
    if 'in:' in query and len(word) == 1:
        i = query.find('in:')
        param_list = query[i + 3:].split(" ")[0]
        if "," in param_list:
            params = param_list.split(',')
            for p in params:
                tasks = in_filter(p, tasks, word[0])
        else:
            tasks = in_filter(param_list, tasks, word[0])

    if 'commenter:' in query:
        i = query.find('commenter:')
        commenter = query[i + 10:].split(" ")[0]
        temp = tasks.filter(event__in=Comment.objects.filter(author__username__contains=commenter.lower())).distinct()
        tasks = temp
    if 'comments:' in query:
        i = query.find('comments:')
        comments = query[i + 9:].split(" ")[0]
        if '>' in comments:
            val = comments[1:]
            temp = [x for x in tasks if len(Comment.objects.filter(task__id=x.id)) > val]
            tasks = temp
        if '<' in comments:
            val = comments[1:]
            temp = [x for x in tasks if len(Comment.objects.filter(task__id=x.id)) < val]
            tasks = temp
        if '..' in comments:
            vals = comments.split("..")
            temp = [x for x in tasks if vals[0] < len(Comment.objects.filter(task__id=x.id)) < vals[1]]
            tasks = temp

    return tasks


def in_filter(p, tasks, word):
    temp = []
    if p == 'title':
        return tasks.filter(Q(title__contains=word.lower())).distinct()
    if p == 'comments':
        return tasks.filter(event__in=Comment.objects.filter(content__contains=word.lower())).distinct()
    return temp

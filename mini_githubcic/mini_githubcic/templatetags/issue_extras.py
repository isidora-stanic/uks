from django import template

register = template.Library()


@register.filter
def is_open(issues, open):
    return issues.filter(is_open=open)


@register.filter(name='another')
def another(tasks, query):
    return tasks, query


@register.filter(name='task_is_open')
def task_is_open(tasksAndQuery, open):
    tasks, query = tasksAndQuery
    if ':pr' in query.lower():
        state = ['OPEN' if open else 'CLOSED']
        return tasks.filter(state=state[0])
    elif ':issue' in query.lower():
        return tasks.filter(is_open=open)
    else:
        state = ['OPEN' if open else 'CLOSED']
        filtered = [x for x in tasks if ('state' in vars(x) and x.state == state[0]) or
                         ('is_open' in vars(x) and x.is_open is open)]

        return filtered

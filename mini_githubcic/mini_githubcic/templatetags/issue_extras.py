from django import template

register = template.Library()


@register.filter
def is_open(issues, open):
    return issues.filter(is_open=open)
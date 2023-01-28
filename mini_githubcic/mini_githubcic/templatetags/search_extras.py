from django import template

register = template.Library()


@register.filter
def len_issues_open(issues, open):
    return len(issues.filter(is_open=open))
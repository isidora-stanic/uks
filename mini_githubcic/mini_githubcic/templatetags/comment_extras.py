from django import template

register = template.Library()


@register.filter
def slice_and_dot(comment):
    return comment[0:8]+"..."



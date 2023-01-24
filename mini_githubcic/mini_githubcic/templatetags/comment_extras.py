from django import template
from mini_githubcic.models import Reaction

register = template.Library()


@register.filter
def slice_and_dot(comment):
    return comment[0:8]+"..."

@register.filter
def len_by_type(reactions, type):
    return len(reactions.filter(type=type))


@register.filter(name='one_more')
def one_more(type, user):
    return type, user


@register.filter(name='is_selected')
def is_selected(typeAndUser, comment):
    type, user = typeAndUser
    return len(Reaction.objects.filter(type=type, user=user, comment=comment)) != 0

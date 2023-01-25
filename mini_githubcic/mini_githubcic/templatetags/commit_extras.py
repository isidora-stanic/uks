from django import template
from dateutil import parser

register = template.Library()


@register.filter
def shorten_sha(sha):
    return sha[0:7]


@register.filter
def replace_slash(value):
    return value.replace("/","%2F")


@register.filter
def bring_back_slash(value):
    return value.replace("%2F", "/")


@register.filter
def convert_str_date(value):
    return parser.parse(value)
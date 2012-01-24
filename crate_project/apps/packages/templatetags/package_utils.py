import os

from django import template

register = template.Library()


@register.filter
def filename(value):
    return os.path.basename(value)


@register.filter
def digest_type(digest):
    return digest.split("$")[0]


@register.filter
def digest_value(digest):
    return digest.split("$")[1]

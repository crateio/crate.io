import os

from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse

from django.conf import settings
from django.utils import formats

import jinja2

from jingo import register
from pinax.apps.account.utils import user_display as pinax_user_display
from staticfiles.storage import staticfiles_storage


@register.function
def ifelse(first, test, nelse):
    return first if test else nelse


@register.function
def pagination_numbers(numbers, current, max_num=13):
    step = (max_num - 1) / 2
    start = numbers.index(current) - step

    if start < 0:
        end = numbers.index(current) + step + abs(start)
        start = 0
    else:
        end = numbers.index(current) + step
    return numbers[start:end + 1]


@register.filter
def reqarg(url, name, value=None):
    parsed = urlparse(url)
    data = parse_qs(parsed.query)
    if value is not None:
        data.update({
            name: [value],
        })
    else:
        if name in data:
            del data[name]

    _data = []
    for key, value in data.iteritems():
        for item in value:
            _data.append((key, item))

    return jinja2.Markup(urlunparse([parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(_data), parsed.fragment]))


@register.filter
def filename(name):
    return os.path.basename(name)


@register.function
def char_split(value, names=None, char="$"):
    value_list = value.split(char)

    if names is not None:
        return dict(zip(names, value_list))

    return value_list


@register.filter
def date(value, arg=None):
    """Formats a date according to the given format."""
    if not value:
        return u''
    if arg is None:
        arg = settings.DATE_FORMAT
    try:
        return formats.date_format(value, arg)
    except AttributeError:
        try:
            return format(value, arg)
        except AttributeError:
            return ''


@register.function
def static(path):
    """
    A template tag that returns the URL to a file
    using staticfiles' storage backend
    """
    return staticfiles_storage.url(path)


@register.filter
def is_checkbox(field):
    return field.field.widget.__class__.__name__.lower() == "checkboxinput"


@register.filter
def css_class(field):
    return field.field.widget.__class__.__name__.lower()


@register.function
def user_display(user):
    return pinax_user_display(user)

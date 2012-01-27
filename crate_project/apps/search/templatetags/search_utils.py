from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="repage")
@stringfilter
def repage(value, new_page):
    parsed = urlparse(value)
    data = parse_qs(parsed.query)
    data.update({
        "page": [new_page],
    })

    _data = []
    for key, value in data.iteritems():
        for item in value:
            _data.append((key, item))

    return urlunparse([parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(_data), parsed.fragment])


@register.filter(name="facet_python")
@stringfilter
def facet_python(value, new):
    parsed = urlparse(value)
    data = parse_qs(parsed.query)
    data.update({
        "python": [new],
    })

    _data = []
    for key, value in data.iteritems():
        for item in value:
            _data.append((key, item))

    return urlunparse([parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(_data), parsed.fragment])

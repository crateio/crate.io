from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


def re_qs(url, key, value):
    parsed = urlparse(url)
    data = parse_qs(parsed.query)
    data.update({
        key: [value],
    })

    _data = []
    for key, value in data.iteritems():
        for item in value:
            _data.append((key, item))

    return urlunparse([parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(_data), parsed.fragment])


@register.filter(name="repage")
@stringfilter
def repage(value, new_page):
    return re_qs(value, "page", new_page)


@register.filter(name="facet_python")
@stringfilter
def facet_python(value, new):
    return re_qs(value, "python", new)


@register.filter(name="facet_os")
@stringfilter
def facet_os(value, new):
    return re_qs(value, "os", new)


@register.filter(name="facet_license")
@stringfilter
def facet_license(value, new):
    return re_qs(value, "license", new)


@register.filter(name="facet_implementation")
@stringfilter
def facet_implementation(value, new):
    return re_qs(value, "implementation", new)

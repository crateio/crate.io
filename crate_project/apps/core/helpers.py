from urllib import urlencode
from urlparse import urlparse, parse_qs, urlunparse

import jinja2

from jingo import register


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

import re

from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.formats import number_format

import jinja2

from jingo import register


@register.filter
def intcomma(value, use_l10n=True):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    if settings.USE_L10N and use_l10n:
        try:
            if not isinstance(value, float):
                value = int(value)
        except (TypeError, ValueError):
            return intcomma(value, False)
        else:
            return jinja2.Markup(number_format(value, force_grouping=True))
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return jinja2.Markup(new)
    else:
        return intcomma(new, use_l10n)

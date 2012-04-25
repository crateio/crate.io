from django.conf import settings

from jingo import register


@register.function
def analytics():
    analytic_codes = {}

    for kind, codes in getattr(settings, "METRON_SETTINGS", {}).items():
        code = codes.get(settings.SITE_ID)
        if code is not None:
            analytic_codes[kind] = code

    return analytic_codes

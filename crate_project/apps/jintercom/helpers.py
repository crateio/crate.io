import time

from django.conf import settings
from django.utils import simplejson
from django.utils.hashcompat import sha_constructor

from jingo import register


@register.function
def intercom_data(user):
    if hasattr(settings, "INTERCOM_APP_ID") and user.is_authenticated():
        if hasattr(settings, "INTERCOM_USER_HASH_KEY"):
            user_hash = sha_constructor(settings.INTERCOM_USER_HASH_KEY + user.email).hexdigest()
        else:
            user_hash = None

        custom_data = {}
        for app in getattr(settings, "INTERCOM_APPS", []):
            m = __import__(app + ".intercom", globals(), locals(), ["intercom"])
            custom_data.update(m.custom_data(user))

        return {
            "app_id": settings.INTERCOM_APP_ID,
            "email": user.email,
            "user_hash": user_hash,
            "created_at": int(time.mktime(user.date_joined.timetuple())),
            "custom_data": simplejson.dumps(custom_data, ensure_ascii=False)
        }
    else:
        return {}

from django.conf import settings
from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from pinax.apps.account.openid_consumer import PinaxConsumer


handler500 = "pinax.views.server_error"


urlpatterns = patterns("",
    url(r"^$", include("search.urls")),
    url(r"^admin/invite_user/$", "pinax.apps.signup_codes.views.admin_invite_user", name="admin_invite_user"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^about/", include("about.urls")),
    url(r"^account/", include("pinax.apps.account.urls")),
    url(r"^openid/", include(PinaxConsumer().urls)),
    url(r"^profiles/", include("idios.urls")),
    # url(r"^notices/", include("notification.urls")),
    url(r"^announcements/", include("announcements.urls")),

    url(r"^packages/", include("packages.urls")),
    url(r"^help/", include("helpdocs.urls"))
)


if settings.SERVE_MEDIA:
    urlpatterns += patterns("",
        url(r"", include("staticfiles.urls")),
    )

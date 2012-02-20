from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard
from admin_tools.utils import get_admin_site_name


class CrateIndexDashboard(Dashboard):

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        self.children.append(modules.LinkList(
            _("Quick links"),
            layout="inline",
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                [_("Return to site"), "/"],
                [_("Change password"),
                 reverse("%s:password_change" % site_name)],
                [_("Log out"), reverse("%s:logout" % site_name)],
            ]
        ))

        # append an app list module for "Administration"
        self.children.append(modules.AppList(
            _("Administration"),
            models=('django.contrib.*',),
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _("Applications"),
            exclude=[
                "django.contrib.*",
                "pinax.apps.*",
                "djcelery.*",
                "emailconfirmation.*",
                "profiles.*",
            ],
        ))

        # append a recent actions module
        self.children.append(modules.RecentActions(_("Recent Actions"), 5))

        # append a feed module
        self.children.append(modules.Feed(
            _("Latest Django News"),
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _("Support"),
            children=[
                {
                    "title": _("Django documentation"),
                    "url": "http://docs.djangoproject.com/",
                    "external": True,
                },
                {
                    "title": _("Django \"django-users\" mailing list"),
                    "url": "http://groups.google.com/group/django-users",
                    "external": True,
                },
                {
                    "title": _("Django irc channel"),
                    "url": "irc://irc.freenode.net/django",
                    "external": True,
                },
            ]
        ))

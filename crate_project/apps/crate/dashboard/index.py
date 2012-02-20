from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard
from admin_tools.utils import get_admin_site_name

from crate.dashboard.modules import StatusModule


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

        self.children.append(StatusModule(_("Status")))

        # append a recent actions module
        self.children.append(modules.RecentActions(_("Recent Actions"), 5))

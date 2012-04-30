from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class List(TimeStampedModel):
    user = models.ForeignKey("auth.User")
    # Translators: This is used to allow naming a specific list of packages.
    name = models.CharField(_("Name"), max_length=50, db_index=True)
    private = models.BooleanField(_("Private"), default=False)

    packages = models.ManyToManyField("packages.Package", verbose_name=_("Packages"))

    class Meta:
        unique_together = ("user", "name")

    def __unicode__(self):
        return u"%(username)s / %(listname)s" % {"username": self.user.username, "listname": self.name}

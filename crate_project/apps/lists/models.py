from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel


class List(TimeStampedModel):
    user = models.ForeignKey("auth.User")
    # Translators: This is used to allow naming a specific list of packages.
    name = models.CharField(_("Name"), max_length=50, db_index=True)
    slug = models.SlugField(max_length=50)

    description = models.CharField(max_length=250, blank=True)

    private = models.BooleanField(_("Private List"), default=False, help_text=_("Private lists are visible only to you."))

    packages = models.ManyToManyField("packages.Package", verbose_name=_("Packages"))

    class Meta:
        unique_together = [
            ("user", "name"),
            ("user", "slug"),
        ]

    def save(self, *args, **kwargs):
        if not self.name:
            raise  IntegrityError("Name cannot be empty")

        if not self.slug:
            slug = slugify(self.name)
            i = 1

            while List.objects.filter(user=self.user, slug=slug).exists():
                slug = slugify(u"%s %s" % (self.name, i))
                i += 1

            self.slug = slug

        return super(List, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"%(username)s / %(listname)s" % {"username": self.user.username, "listname": self.name}

    def get_absolute_url(self):
        return reverse("lists_detail", kwargs={"username": self.user.username, "slug": self.slug})

from django.db import models

from model_utils.models import TimeStampedModel


class Favorite(TimeStampedModel):

    user = models.ForeignKey("auth.User")
    package = models.ForeignKey("packages.Package")

    class Meta:
        unique_together = ("user", "package")

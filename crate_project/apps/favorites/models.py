from django.db import models

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from model_utils.models import TimeStampedModel


class Favorite(TimeStampedModel):

    user = models.ForeignKey("auth.User")

    content_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey("content_type", "object_id")

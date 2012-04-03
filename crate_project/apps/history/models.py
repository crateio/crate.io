from django.db import models

from jsonfield import JSONField
from model_utils import Choices
from model_utils.models import TimeStampedModel


class Event(TimeStampedModel):

    ACTIONS = Choices(
            ("package_create", "Package Created"),
            ("package_delete", "Package Deleted"),
            ("release_create", "Release Created"),
            ("release_delete", "Release Deleted"),
            ("file_add", "File Added"),
            ("file_remove", "File Removed"),
        )

    package = models.SlugField(max_length=150)
    version = models.CharField(max_length=512)

    action = models.CharField(max_length=25, choices=ACTIONS)

    data = JSONField()

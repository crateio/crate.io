from django.db import models

from idios.models import ProfileBase


class Profile(ProfileBase):
    name = models.CharField("name", max_length=50, null=True, blank=True)
    about = models.TextField("about", null=True, blank=True)
    location = models.CharField("location", max_length=40, null=True, blank=True)
    website = models.URLField("website", null=True, blank=True, verify_exists=False)

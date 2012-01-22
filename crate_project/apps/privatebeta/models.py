from django.db import models

from django.utils.timezone import now


class WaitingList(models.Model):
    email = models.EmailField(unique=True)
    invited = models.BooleanField(default=False)
    when = models.DateTimeField(default=now)

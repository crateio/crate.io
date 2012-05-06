from django.conf import settings
from django.core.management.base import BaseCommand

from django.contrib.auth.models import User

from account.models import EmailAddress


class Command(BaseCommand):

    def handle(self, *args, **options):
        for u in User.objects.all():
            EmailAddress.objects.create(user=u, email=u.email, verified=True, primary=True)

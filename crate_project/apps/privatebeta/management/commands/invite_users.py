from django.core.management.base import NoArgsCommand

from pinax.apps.signup_codes.models import SignupCode
from privatebeta.models import WaitingList


class Command(NoArgsCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle_noargs(self, **options):
        count = 0
        for wl in WaitingList.objects.filter(invited=False):
            sc = SignupCode.create(wl.email, 24 * 14)
            sc.send()

            wl.invited = True
            wl.save()

            count += 1

        print "Invited %s Users" % count

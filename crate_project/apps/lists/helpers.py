from jingo import register

from lists.models import List


@register.function
def lists_for_user(user):
    if user.is_authenticated():
        return List.objects.filter(user=user).prefetch_related("packages")

    return []

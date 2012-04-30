from jingo import register

from lists.forms import CreateListForm
from lists.models import List


@register.function
def lists_for_user(user):
    if user.is_authenticated():
        return List.objects.filter(user=user).prefetch_related("packages")

    return []

@register.function
def new_list_with_package_form():
    return CreateListForm()

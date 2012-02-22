import copy

from django import template

from favorites.models import Favorite

register = template.Library()


@register.inclusion_tag("favorites/widget.html", takes_context=True)
def favorite(context, obj):
    ctx = copy.copy(context)

    if context["request"].user.is_authenticated():
        followed = Favorite.objects.filter(package=obj, user=context["request"].user).exists()
    else:
        followed = False

    ctx.update({
        "object": obj,
        "followed": followed,
    })
    return ctx

import copy

from django import template

from favorites.models import Favorite

register = template.Library()


@register.inclusion_tag("favorites/widget.html", takes_context=True)
def favorite(context, obj):
    ctx = copy.copy(context)
    ctx.update({
        "object": obj,
        "followed": Favorite.objects.filter(package=obj, user=context["request"].user).exists(),
    })
    return ctx

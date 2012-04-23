from favorites.models import Favorite
from jingo import register


@register.function
def favorite_info(user, obj):
    if user.is_authenticated():
        followed = Favorite.objects.filter(package=obj, user=user).exists()
    else:
        followed = False

    return {
        "followed": followed,
        "object": obj,
    }

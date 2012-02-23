from django.contrib import admin

from favorites.models import Favorite


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "package", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["user__username", "package__name"]
    raw_id_fields = ["user", "package"]

admin.site.register(Favorite, FavoriteAdmin)

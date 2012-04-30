from django.contrib import admin

from lists.models import List


class PackageInline(admin.TabularInline):
    model = List.packages.through
    raw_id_fields = ["package"]
    extra = 0


class ListAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["name", "user__username", "packages__name"]
    raw_id_fields = ["user"]
    exclude = ["packages"]

    inlines = [
        PackageInline,
    ]

admin.site.register(List, ListAdmin)

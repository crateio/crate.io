from django.contrib import admin

from history.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ["package", "version", "action", "data", "created"]
    list_filter = ["action", "created"]
    search_fields = ["package", "version"]


admin.site.register(Event, EventAdmin)

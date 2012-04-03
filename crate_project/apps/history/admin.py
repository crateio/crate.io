from django.contrib import admin

from history.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ["package", "version", "data", "created"]
    list_filter = ["created"]
    search_fields = ["package", "version"]


admin.register(Event, EventAdmin)

from django.contrib import admin

from privatebeta.models import WaitingList


class WaitingListAdmin(admin.ModelAdmin):
    list_display = ["email", "when", "invited"]
    list_filter = ["invited", "when"]
    search_fields = ["email"]

admin.site.register(WaitingList, WaitingListAdmin)

from django.contrib import admin

from pypi.models import ChangeLog, Log, PackageModified


class ChangeLogAdmin(admin.ModelAdmin):
    list_display = ["package", "version", "timestamp", "action", "handled"]
    list_filter = ["timestamp", "handled"]
    search_fields = ["package", "action"]


class LogAdmin(admin.ModelAdmin):
    list_display = ["type", "created", "message"]
    list_filter = ["type", "created"]


class PackageModifiedAdmin(admin.ModelAdmin):
    list_display = ["url", "md5", "last_modified", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["url", "md5"]
    raw_id_fields = ["release_file"]


admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(PackageModified, PackageModifiedAdmin)

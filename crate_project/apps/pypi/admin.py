from django.contrib import admin

from pypi.models import ChangeLog, Log, PackageModified, TaskLog


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


class TaskLogAdmin(admin.ModelAdmin):
    list_display = ["task_id", "status", "name", "created", "modified"]
    list_filter = ["status", "name", "created", "modified"]
    search_fields = ["task_id"]


admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(PackageModified, PackageModifiedAdmin)
admin.site.register(TaskLog, TaskLogAdmin)

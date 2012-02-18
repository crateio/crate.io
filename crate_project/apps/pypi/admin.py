from django.contrib import admin

from pypi.models import PyPIMirrorPage
from pypi.models import ChangeLog, Log, PackageModified, TaskLog, DownloadChange


class PyPIMirrorPageAdmin(admin.ModelAdmin):
    list_display = ["package", "type"]
    list_filter = ["type"]
    search_fields = ["package__name", "content"]
    raw_id_fields = ["package"]


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
    search_fields = ["task_id", "args", "kwargs"]


class DownloadChangeAdmin(admin.ModelAdmin):
    list_display = ["release", "change", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["release__package__name"]


admin.site.register(PyPIMirrorPage, PyPIMirrorPageAdmin)
admin.site.register(ChangeLog, ChangeLogAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(PackageModified, PackageModifiedAdmin)
admin.site.register(TaskLog, TaskLogAdmin)
admin.site.register(DownloadChange, DownloadChangeAdmin)

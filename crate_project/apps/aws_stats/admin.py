from django.contrib import admin

from aws_stats.models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ["when", "method", "status", "host", "uri_stem", "uri_query", "ip", "edge_location"]
    list_filter = ["when", "method", "status", "edge_location"]
    search_fields = ["host", "uri_stem", "uri_query", "ip", "referer", "user_agent"]


admin.site.register(Log, LogAdmin)

from django.contrib import admin

from pypi.models import PyPIMirrorPage, PyPIServerSigPage, PyPIIndexPage
from pypi.models import PyPIDownloadChange


class PyPIMirrorPageAdmin(admin.ModelAdmin):
    list_display = ["package", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["package__name", "content"]
    raw_id_fields = ["package"]


class PyPIServerSigPageAdmin(admin.ModelAdmin):
    list_display = ["package", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["package__name", "content"]
    raw_id_fields = ["package"]


class PyPIIndexPageAdmin(admin.ModelAdmin):
    list_display = ["created", "modified"]
    list_filter = ["created", "modified"]


class PyPIDownloadChangeAdmin(admin.ModelAdmin):
    list_display = ["file", "change", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["file__release__package__name"]
    raw_id_fields = ["file"]


admin.site.register(PyPIMirrorPage, PyPIMirrorPageAdmin)
admin.site.register(PyPIServerSigPage, PyPIServerSigPageAdmin)
admin.site.register(PyPIIndexPage, PyPIIndexPageAdmin)
admin.site.register(PyPIDownloadChange, PyPIDownloadChangeAdmin)

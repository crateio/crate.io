from django.contrib import admin

from packages.models import Package, Release, ReleaseFile, TroveClassifier
from packages.models import ReleaseRequire, ReleaseProvide, ReleaseObsolete, ReleaseURI


class PackageAdmin(admin.ModelAdmin):
    list_display = ["name", "created", "modified"]
    list_filter = ["created", "modified"]
    search_fields = ["name"]


class ReleaseRequireInline(admin.TabularInline):
    model = ReleaseRequire
    extra = 0


class ReleaseProvideInline(admin.TabularInline):
    model = ReleaseProvide
    extra = 0


class ReleaseObsoleteInline(admin.TabularInline):
    model = ReleaseObsolete
    extra = 0


class ReleaseFileInline(admin.TabularInline):
    model = ReleaseFile
    extra = 0


class ReleaseURIInline(admin.TabularInline):
    model = ReleaseURI
    extra = 0


class ReleaseAdmin(admin.ModelAdmin):
    inlines = [ReleaseURIInline, ReleaseFileInline, ReleaseRequireInline, ReleaseProvideInline, ReleaseObsoleteInline]
    list_display = ["__unicode__", "package", "version", "summary", "author", "author_email", "maintainer", "maintainer_email", "created", "modified"]
    list_filter = ["created", "modified", "hidden"]
    search_fields = ["package__name", "version", "summary", "author", "author_email", "maintainer", "maintainer_email"]
    raw_id_fields = ["package"]


class TroveClassifierAdmin(admin.ModelAdmin):
    list_display = ["trove"]
    search_fields = ["trove"]


class ReleaseFileAdmin(admin.ModelAdmin):
    list_display = ["release", "type", "python_version", "downloads", "comment", "created", "modified"]
    list_filter = ["type", "created", "modified"]
    search_fields = ["release__package__name", "filename", "digest"]
    raw_id_fields = ["release"]


admin.site.register(Package, PackageAdmin)
admin.site.register(Release, ReleaseAdmin)
admin.site.register(ReleaseFile, ReleaseFileAdmin)
admin.site.register(TroveClassifier, TroveClassifierAdmin)

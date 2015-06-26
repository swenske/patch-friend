from django.contrib import admin

from .models import *

class BinaryPackageInline(admin.StackedInline):
    model = BinaryPackage
    extra = 0

class SourcePackageInline(admin.StackedInline):
    model = SourcePackage
    extra = 0

class AdvisoryAdmin(admin.ModelAdmin):
    inlines = [SourcePackageInline, BinaryPackageInline]
    list_filter = ['issued']   
    search_fields = ['debian_id']
    list_display = ['upstream_id', 'short_description', 'source_package_names', 'issued']

admin.site.register(Advisory, AdvisoryAdmin)
from django.contrib import admin

from .models import Tenant, Source, ImportBatch, NormalizedRecord, AuditEntry


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'tenant', 'created_at']
    list_filter = ['source_type', 'tenant']


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'source_type', 'filename', 'received_at', 'status']
    list_filter = ['source_type', 'status']


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'record_type', 'category', 'emission_scope', 'status', 'approved_at']
    list_filter = ['record_type', 'emission_scope', 'status']
    search_fields = ['category', 'vendor', 'location']


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'record', 'event_type', 'created_by', 'created_at']
    list_filter = ['event_type']

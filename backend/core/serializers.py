from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Tenant, Source, ImportBatch, NormalizedRecord, AuditEntry

User = get_user_model()


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'created_at']


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id', 'name', 'source_type', 'config', 'created_at']


class ImportBatchSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)

    class Meta:
        model = ImportBatch
        fields = ['id', 'source', 'source_type', 'filename', 'received_at', 'row_count', 'imported_count', 'failed_count', 'status']


class NormalizedRecordSerializer(serializers.ModelSerializer):
    source = SourceSerializer(read_only=True)
    tenant = TenantSerializer(read_only=True)
    approved_by = serializers.StringRelatedField(read_only=True)
    last_editor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NormalizedRecord
        fields = [
            'id', 'tenant', 'source', 'import_batch', 'record_type', 'category', 'emission_scope',
            'activity_start', 'activity_end', 'vendor', 'location', 'quantity', 'quantity_unit',
            'normalized_quantity', 'normalized_unit', 'emissions_kg_co2e', 'status', 'suspicious_reason',
            'approved_by', 'approved_at', 'last_editor', 'updated_at', 'raw_payload',
        ]
        read_only_fields = ['id', 'tenant', 'source', 'import_batch', 'normalized_quantity', 'normalized_unit', 'approved_by', 'approved_at', 'last_editor', 'updated_at']


class AuditEntrySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AuditEntry
        fields = ['id', 'record', 'event_type', 'created_by', 'created_at', 'data']

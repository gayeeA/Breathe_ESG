from django.conf import settings
from django.db import models
from django.utils import timezone

USER_MODEL = settings.AUTH_USER_MODEL

SOURCE_TYPE_CHOICES = [
    ('sap-fuel', 'SAP fuel/procurement'),
    ('utility-electricity', 'Utility electricity'),
    ('travel-corporate', 'Corporate travel'),
]
STATUS_CHOICES = [
    ('processing', 'Processing'),
    ('complete', 'Complete'),
    ('failed', 'Failed'),
]
RECORD_STATUS_CHOICES = [
    ('pending_review', 'Pending review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]
EMISSION_SCOPE_CHOICES = [
    ('scope1', 'Scope 1'),
    ('scope2', 'Scope 2'),
    ('scope3', 'Scope 3'),
]


class Tenant(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sources')
    name = models.CharField(max_length=128)
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPE_CHOICES)
    config = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.source_type})'


class ImportBatch(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='imports')
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, related_name='imports')
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPE_CHOICES)
    filename = models.CharField(max_length=255)
    received_at = models.DateTimeField(auto_now_add=True)
    row_count = models.PositiveIntegerField(default=0)
    imported_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='processing')

    def __str__(self):
        return f'Import {self.id} {self.source_type} ({self.received_at:%Y-%m-%d})'


class NormalizedRecord(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='records')
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, related_name='records')
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.SET_NULL, null=True, related_name='records')
    raw_payload = models.JSONField(default=dict)

    record_type = models.CharField(max_length=32)
    category = models.CharField(max_length=128)
    emission_scope = models.CharField(max_length=16, choices=EMISSION_SCOPE_CHOICES)
    activity_start = models.DateField(null=True, blank=True)
    activity_end = models.DateField(null=True, blank=True)
    vendor = models.CharField(max_length=128, blank=True)
    location = models.CharField(max_length=128, blank=True)

    quantity = models.FloatField(null=True, blank=True)
    quantity_unit = models.CharField(max_length=32, blank=True)
    normalized_quantity = models.FloatField(default=0.0)
    normalized_unit = models.CharField(max_length=32, blank=True)
    emissions_kg_co2e = models.FloatField(default=0.0)

    suspicious_reason = models.CharField(max_length=256, blank=True)
    status = models.CharField(max_length=24, choices=RECORD_STATUS_CHOICES, default='pending_review')
    approved_by = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_records')
    approved_at = models.DateTimeField(null=True, blank=True)
    last_editor = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.record_type} {self.category} ({self.status})'


class AuditEntry(models.Model):
    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='audit_entries')
    event_type = models.CharField(max_length=64)
    created_by = models.ForeignKey(USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f'{self.event_type} for record {self.record_id}'

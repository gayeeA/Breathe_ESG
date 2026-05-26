import io
import csv
from django.db.models import Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import AllowAny
from .models import Tenant, Source, ImportBatch, NormalizedRecord, AuditEntry
from .serializers import TenantSerializer, NormalizedRecordSerializer
from .utils import SUPPORTED_SOURCE_TYPES, read_csv_rows, normalize_row_for_source
from rest_framework.decorators import action

class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenant.objects.all().order_by('name')
    serializer_class = TenantSerializer


class NormalizedRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = NormalizedRecord.objects.all().order_by('-created_at')
    serializer_class = NormalizedRecordSerializer
    pagination_class = None
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        tenant_slug = self.request.query_params.get('tenant')
        record_type = self.request.query_params.get('record_type')
        if status_param:
            queryset = queryset.filter(status=status_param)
        if tenant_slug:
            queryset = queryset.filter(tenant__slug=tenant_slug)
        if record_type:   # ✅ NEW
            queryset = queryset.filter(record_type__icontains=record_type)    
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        record.status = 'approved'
        record.approved_at = timezone.now()
        record.approved_by = None   # remove user dependency
        record.save(update_fields=['status', 'approved_at', 'approved_by'])

        AuditEntry.objects.create(
            record=record,
            event_type='approved',
            created_by=None,
            data={'status': record.status},
        )

        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        record = self.get_object()
        reason = request.data.get('reason', '')

        record.status = 'rejected'
        record.rejection_reason = reason
        record.save(update_fields=['status', 'rejection_reason'])

        return Response({'status': 'rejected', 'reason': reason})
@method_decorator(csrf_exempt, name='dispatch')
class ImportUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        source_type = request.data.get('source_type')
        tenant_slug = request.data.get('tenant', 'default')
        file_obj = request.FILES.get('file')

        if not file_obj:
            return Response({'detail': 'Missing file upload.'}, status=status.HTTP_400_BAD_REQUEST)
        if source_type not in SUPPORTED_SOURCE_TYPES:
            return Response({'detail': 'Unsupported source_type.'}, status=status.HTTP_400_BAD_REQUEST)

        tenant, _ = Tenant.objects.get_or_create(slug=tenant_slug, defaults={'name': tenant_slug.title()})
        source, _ = Source.objects.get_or_create(
            tenant=tenant,
            source_type=source_type,
            defaults={'name': source_type.replace('-', ' ').title()},
        )

        batch = ImportBatch.objects.create(
            tenant=tenant,
            source=source,
            source_type=source_type,
            filename=file_obj.name,
            status='processing',
        )

        text_io = io.TextIOWrapper(file_obj.file, encoding='utf-8-sig', newline='')
        rows = read_csv_rows(text_io)
        imported = 0
        failed = 0

        for index, row in enumerate(rows, start=1):
            normalized = normalize_row_for_source(source_type, row)
            if not normalized:
                failed += 1
                continue

            NormalizedRecord.objects.create(
                tenant=tenant,
                source=source,
                import_batch=batch,
                raw_payload=normalized.get('raw_payload', row),
                record_type=normalized.get('record_type'),
                category=normalized.get('category'),
                emission_scope=normalized.get('emission_scope'),

                activity_start=normalized.get('activity_start'),
                activity_end=normalized.get('activity_end'),

                vendor=normalized.get('vendor'),
                location=normalized.get('location'),

                quantity=normalized.get('quantity') or 0,
                quantity_unit=normalized.get('quantity_unit'),

                normalized_quantity=normalized.get('normalized_quantity') or 0,
                normalized_unit=normalized.get('normalized_unit'),

                emissions_kg_co2e=normalized.get('emissions_kg_co2e') or 0,

                suspicious_reason=normalized.get('suspicious_reason') or '',
            )
            imported += 1

        batch.row_count = len(rows)
        batch.imported_count = imported
        batch.failed_count = failed
        batch.status = 'complete'
        batch.save()

        return Response({'imported': imported, 'failed': failed, 'row_count': len(rows)})

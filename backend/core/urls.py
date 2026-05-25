from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TenantViewSet, NormalizedRecordViewSet, ImportUploadView

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'records', NormalizedRecordViewSet, basename='record')

urlpatterns = [
    path('', include(router.urls)),
    path('imports/upload/', ImportUploadView.as_view(), name='import-upload'),
]

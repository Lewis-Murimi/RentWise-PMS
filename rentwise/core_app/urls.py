from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserViewSet, PropertyViewSet, UnitViewSet, TenantProfileViewSet,
    CaretakerProfileViewSet, PaymentViewSet, MaintenanceRequestViewSet,
    CustomTokenObtainPairView, CurrentUserView,
    AssignManagerToPropertyView, AssignCaretakerToPropertyView, AssignUnitToTenantView,
    VacateUnitFromTenantView, UnassignCaretakerFromPropertyView, UnassignManagerFromPropertyView,
    TenantsByPropertyView, UnitsByPropertyView, PaymentsByPropertyView,
    MaintenanceByPropertyView, PaymentsByTenantView
)

# Register viewsets with DefaultRouter
router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('properties', PropertyViewSet, basename='property')
router.register('units', UnitViewSet, basename='unit')
router.register('tenants', TenantProfileViewSet, basename='tenant')
router.register('caretakers', CaretakerProfileViewSet, basename='caretaker')
router.register('payments', PaymentViewSet, basename='payment')
router.register('maintenance', MaintenanceRequestViewSet, basename='maintenance')

urlpatterns = [
    # Viewsets under /api/
    path('', include(router.urls)),

    # JWT auth endpoints
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Current user profile endpoint
    path('me/', CurrentUserView.as_view(), name='current_user'),

    # Assignment / unassignment endpoints
    path('assign/manager/', AssignManagerToPropertyView.as_view(), name='assign_manager'),
    path('assign/caretaker/', AssignCaretakerToPropertyView.as_view(), name='assign_caretaker'),
    path('assign/unit/', AssignUnitToTenantView.as_view(), name='assign_unit'),

    path('vacate/unit/', VacateUnitFromTenantView.as_view(), name='vacate_unit'),
    path('unassign/caretaker/', UnassignCaretakerFromPropertyView.as_view(), name='unassign_caretaker'),
    path('unassign/manager/', UnassignManagerFromPropertyView.as_view(), name='unassign_manager'),

    # Property-specific queries
    path('properties/<int:property_id>/tenants/', TenantsByPropertyView.as_view(), name='tenants_by_property'),
    path('properties/<int:property_id>/units/', UnitsByPropertyView.as_view(), name='units_by_property'),
    path('properties/<int:property_id>/payments/', PaymentsByPropertyView.as_view(), name='payments_by_property'),
    path('properties/<int:property_id>/maintenance/', MaintenanceByPropertyView.as_view(), name='maintenance_by_property'),

    # Payments by tenant
    path('tenants/<int:tenant_id>/payments/', PaymentsByTenantView.as_view(), name='payments_by_tenant'),
]

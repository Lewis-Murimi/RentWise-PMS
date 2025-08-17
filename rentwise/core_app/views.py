from rest_framework import viewsets, permissions
from .models import User, Property, Unit, TenantProfile, CaretakerProfile, Payment, MaintenanceRequest
from .serializers import (
    UserSerializer, PropertySerializer, UnitSerializer,
    TenantProfileSerializer, CaretakerProfileSerializer,
    PaymentSerializer, MaintenanceRequestSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]



class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Property.objects.none()
        if getattr(user, 'role', None) in ['landlord', 'manager']:
            return Property.objects.filter(owner=user)
        return Property.objects.none()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Unit.objects.none()
        role = getattr(user, 'role', None)
        if role in ['landlord', 'manager']:
            return Unit.objects.filter(property__owner=user)
        elif role == 'tenant':
            tenant_profile = getattr(user, 'tenant_profile', None)
            if tenant_profile:
                return tenant_profile.units.all()
        return Unit.objects.none()



class TenantProfileViewSet(viewsets.ModelViewSet):
    queryset = TenantProfile.objects.all()
    serializer_class = TenantProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TenantProfile.objects.none()
        role = getattr(user, 'role', None)
        if role == 'tenant':
            return TenantProfile.objects.filter(user=user)
        elif role in ['landlord', 'manager']:
            return TenantProfile.objects.filter(units__property__owner=user).distinct()
        return TenantProfile.objects.none()


class CaretakerProfileViewSet(viewsets.ModelViewSet):
    queryset = CaretakerProfile.objects.all()
    serializer_class = CaretakerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return CaretakerProfile.objects.none()
        role = getattr(user, 'role', None)
        if role in ['caretaker', 'manager', 'landlord']:
            return CaretakerProfile.objects.all()
        return CaretakerProfile.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        role = getattr(user, 'role', None)
        if role == 'tenant':
            return Payment.objects.filter(tenant__user=user)
        elif role in ['landlord', 'manager']:
            return Payment.objects.filter(tenant__units__property__owner=user).distinct()
        return Payment.objects.none()



class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return MaintenanceRequest.objects.none()
        role = getattr(user, 'role', None)
        if role == 'tenant':
            return MaintenanceRequest.objects.filter(tenant__user=user)
        elif role in ['landlord', 'manager', 'caretaker']:
            return MaintenanceRequest.objects.filter(tenant__units__property__owner=user).distinct()
        return MaintenanceRequest.objects.none()

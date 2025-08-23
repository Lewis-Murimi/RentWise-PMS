from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    User, Property, Unit, TenantProfile, CaretakerProfile,
    Payment, MaintenanceRequest, ManagerProfile, TenantUnit
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'role', 'phone_number', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class CurrentUserSerializer(serializers.ModelSerializer):
    tenant_profile = serializers.SerializerMethodField()
    manager_profile = serializers.SerializerMethodField()
    caretaker_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email", "phone_number",
            "role", "tenant_profile", "manager_profile", "caretaker_profile"
        ]

    @staticmethod
    def get_tenant_profile(obj):
        if obj.role == 'tenant' and hasattr(obj, 'tenant_profile'):
            return TenantProfileSerializer(obj.tenant_profile).data
        return None

    @staticmethod
    def get_manager_profile(obj):
        if obj.role == 'property_manager' and hasattr(obj, 'manager_profile'):
            return ManagerProfileSerializer(obj.manager_profile).data
        return None

    @staticmethod
    def get_caretaker_profile(obj):
        if obj.role == 'caretaker' and hasattr(obj, 'caretaker_profile'):
            return CaretakerProfileSerializer(obj.caretaker_profile).data
        return None



class UnitSerializer(serializers.ModelSerializer):
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(),
        source='property',
        write_only=True
    )

    class Meta:
        model = Unit
        fields = ['id', 'unit_number', 'size', 'rent', 'status', 'property_id']


class PropertySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='owner', write_only=True,required=False
    )
    units = UnitSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'address', 'description', 'type',
            'owner', 'owner_id', 'units',
            'created_at', 'updated_at'
        ]


class TenantProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    units = UnitSerializer(many=True, read_only=True)
    unit_ids = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(), many=True, source='units', write_only=True
    )

    class Meta:
        model = TenantUnit
        fields = [
            'id', 'user', 'user_id', 'units', 'unit_ids',
            'move_in_date', 'move_out_date'
        ]


class ManagerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    managed_properties = PropertySerializer(many=True, read_only=True)
    managed_property_ids = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), many=True,
        source='managed_properties', write_only=True
    )

    class Meta:
        model = ManagerProfile
        fields = [
            'id', 'user', 'user_id',
            'managed_properties', 'managed_property_ids'
        ]


class CaretakerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    assigned_property = PropertySerializer(read_only=True)
    assigned_property_id = serializers.PrimaryKeyRelatedField(
        queryset=Property.objects.all(), source='assigned_property',
        write_only=True, allow_null=True
    )

    class Meta:
        model = CaretakerProfile
        fields = [
            'id', 'user', 'user_id',
            'assigned_property', 'assigned_property_id'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    tenant = TenantProfileSerializer(read_only=True)
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=TenantProfile.objects.all(), source='tenant', write_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id', 'tenant', 'tenant_id',
            'amount', 'due_date', 'payment_date',
            'status', 'created_at', 'updated_at'
        ]


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    tenant = TenantProfileSerializer(read_only=True)
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=TenantProfile.objects.all(), source='tenant', write_only=True
    )

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'tenant', 'tenant_id',
            'description', 'request_date',
            'completion_date', 'status'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError(
                {"detail": "Must include 'email' and 'password'."}
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials, try again."})

        data = super().validate(attrs)

        # Add custom response data
        data.update({
            "id": user.id,
            "email": user.email,
            "role": getattr(user, "role", None),
            "first_name": user.first_name,
            "last_name": user.last_name,
        })

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["id"] = user.id
        token["email"] = user.email
        token["role"] = getattr(user, "role", None)
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token
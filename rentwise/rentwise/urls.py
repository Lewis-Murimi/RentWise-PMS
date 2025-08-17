"""
URL configuration for rentwise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rentwise.core_app.views import (
    UserViewSet, PropertyViewSet, UnitViewSet, TenantProfileViewSet,
    CaretakerProfileViewSet, PaymentViewSet, MaintenanceRequestViewSet
)

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('properties', PropertyViewSet)
router.register('units', UnitViewSet)
router.register('tenants', TenantProfileViewSet)
router.register('caretakers', CaretakerProfileViewSet)
router.register('payments', PaymentViewSet)
router.register('maintenance', MaintenanceRequestViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

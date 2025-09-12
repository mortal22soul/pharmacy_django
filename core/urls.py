from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (PharmacyViewSet, PatientViewSet, MedicineViewSet,
                    PharmacyInventoryViewSet, PatientPurchaseViewSet,
                    PatientInteractionLogViewSet, PharmaciesNearbyView)

router = DefaultRouter()
router.register('pharmacies', PharmacyViewSet)
router.register('patients', PatientViewSet)
router.register('medicines', MedicineViewSet)
router.register('inventory', PharmacyInventoryViewSet)
router.register('purchases', PatientPurchaseViewSet)
router.register('interactions', PatientInteractionLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pharmacies/nearby/', PharmaciesNearbyView.as_view(), name='pharmacies-nearby'),
]

from django.shortcuts import render

from decimal import Decimal
from django.db import transaction
from django.db.models import F, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import (Pharmacy, Patient, Medicine, PharmacyInventory, PatientPurchase, PatientInteractionLog)
from .serializers import (PharmacySerializer, PatientSerializer, MedicineSerializer,
                        PharmacyInventorySerializer, PatientPurchaseSerializer,
                        PatientInteractionLogSerializer)

from .filters import PharmacyInventoryFilter

import math

# Create your views here.

class PharmacyViewSet(viewsets.ModelViewSet):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'address']
    ordering_fields = ['name']

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['phone_number', 'name']

class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'manufacturer']

class PharmacyInventoryViewSet(viewsets.ModelViewSet):
    queryset = PharmacyInventory.objects.select_related('pharmacy', 'medicine').all()
    serializer_class = PharmacyInventorySerializer
    filterset_class = PharmacyInventoryFilter

class PatientInteractionLogViewSet(viewsets.ModelViewSet):
    queryset = PatientInteractionLog.objects.select_related('patient','pharmacy','medicine').all()
    serializer_class = PatientInteractionLogSerializer

class PatientPurchaseViewSet(viewsets.ModelViewSet):
    queryset = PatientPurchase.objects.select_related('patient','pharmacy','medicine').all()
    serializer_class = PatientPurchaseSerializer

    def create(self, request, *args, **kwargs):
        """
        Custom create: atomically check & decrement inventory stock, snapshot price.
        Expected payload:
        {
        "patient": 1,
        "pharmacy": 1,
        "medicine": 1,
        "quantity": 2
        }
        """
        data = request.data.copy()
        quantity = int(data.get('quantity', 0))
        pharmacy_id = data.get('pharmacy')
        medicine_id = data.get('medicine')
        patient_id = data.get('patient')

        if not (pharmacy_id and medicine_id and patient_id and quantity > 0):
            return Response({"detail": "patient, pharmacy, medicine and quantity (>0) are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Lock the inventory row for update
                inv = PharmacyInventory.objects.select_for_update().get(pharmacy_id=pharmacy_id, medicine_id=medicine_id)
                if inv.stock_quantity < quantity:
                    return Response({"detail": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)
                # Decrement
                inv.stock_quantity = F('stock_quantity') - quantity
                inv.save()
                inv.refresh_from_db()

                # Snapshot unit price
                unit_price = inv.price

                purchase = PatientPurchase.objects.create(
                    patient_id=patient_id,
                    pharmacy_id=pharmacy_id,
                    medicine_id=medicine_id,
                    quantity=quantity,
                    price=unit_price
                )
                serializer = self.get_serializer(purchase)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except PharmacyInventory.DoesNotExist:
            return Response({"detail": "Inventory record not found for this pharmacy & medicine."}, status=status.HTTP_400_BAD_REQUEST)

# Utility: Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    # lat/lon in decimal degrees
    R = 6371  # km
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    dphi = math.radians(float(lat2) - float(lat1))
    dlambda = math.radians(float(lon2) - float(lon1))
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

from rest_framework.views import APIView

class PharmaciesNearbyView(APIView):
    """
    GET /api/pharmacies/nearby/?lat=...&lng=...&medicine=aspirin (medicine by id or name)
    Returns pharmacies ordered by distance that have stock > 0 for the medicine.
    """
    def get(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        medicine_q = request.query_params.get('medicine')  # id or part of name

        if not (lat and lng and medicine_q):
            return Response({"detail": "Provide lat, lng, and medicine (id or name)."}, status=400)

        # find medicine(s)
        meds = Medicine.objects.filter(Q(id=medicine_q) | Q(name__icontains=medicine_q))
        if not meds.exists():
            return Response({"detail": "Medicine not found."}, status=404)

        med_ids = list(meds.values_list('id', flat=True))

        # find inventories with stock > 0
        inv_qs = PharmacyInventory.objects.select_related('pharmacy','medicine').filter(medicine_id__in=med_ids, stock_quantity__gt=0)

        results = []
        for inv in inv_qs:
            ph = inv.pharmacy
            if ph.latitude is None or ph.longitude is None:
                continue
            dist = haversine(lat, lng, ph.latitude, ph.longitude)
            results.append({
                "pharmacy_id": ph.id,
                "pharmacy_name": ph.name,
                "address": ph.address,
                "distance_km": round(dist, 3),
                "stock_quantity": inv.stock_quantity,
                "price": str(inv.price),
                "medicine_id": inv.medicine.id,
                "medicine_name": inv.medicine.name,
            })
        results = sorted(results, key=lambda x: x['distance_km'])
        return Response(results)

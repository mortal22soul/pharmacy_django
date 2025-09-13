from rest_framework import serializers
from .models import (Pharmacy, Patient, Medicine, PharmacyInventory,PatientPurchase, PatientInteractionLog)

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'

class PharmacyInventorySerializer(serializers.ModelSerializer):
    pharmacy = PharmacySerializer(read_only=True)
    medicine = MedicineSerializer(read_only=True)
    pharmacy_id = serializers.PrimaryKeyRelatedField(queryset=Pharmacy.objects.all(), source='pharmacy', write_only=True)
    medicine_id = serializers.PrimaryKeyRelatedField(queryset=Medicine.objects.all(), source='medicine', write_only=True)

    class Meta:
        model = PharmacyInventory
        fields = ['id', 'pharmacy', 'medicine', 'pharmacy_id', 'medicine_id', 'stock_quantity', 'price', 'created_at', 'updated_at']

class PatientPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPurchase
        fields = '__all__'
        read_only_fields = ['price', 'created_at']  # price will be set server-side

class PatientInteractionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientInteractionLog
        fields = '__all__'

class PharmacyNearbySerializer(serializers.Serializer):
    pharmacy_id = serializers.IntegerField()
    pharmacy_name = serializers.CharField()
    address = serializers.CharField()
    distance_km = serializers.FloatField()
    stock_quantity = serializers.IntegerField()
    price = serializers.CharField()   # or DecimalField(max_digits=10, decimal_places=2)
    medicine_id = serializers.IntegerField()
    medicine_name = serializers.CharField()

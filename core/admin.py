from django.contrib import admin
from .models import Pharmacy, Patient, Medicine, PharmacyInventory, PatientPurchase, PatientInteractionLog

# Register your models here.

admin.site.register(Pharmacy)
admin.site.register(Patient)
admin.site.register(Medicine)
admin.site.register(PharmacyInventory)
admin.site.register(PatientPurchase)
admin.site.register(PatientInteractionLog)

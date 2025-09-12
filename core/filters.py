import django_filters
from .models import PharmacyInventory, Pharmacy, Medicine

class PharmacyInventoryFilter(django_filters.FilterSet):
    pharmacy = django_filters.NumberFilter(field_name='pharmacy__id')
    medicine = django_filters.NumberFilter(field_name='medicine__id')
    class Meta:
        model = PharmacyInventory
        fields = ['pharmacy', 'medicine']

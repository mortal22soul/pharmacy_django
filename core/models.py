from django.db import models
from django.utils import timezone

# Create your models here.

class Pharmacy(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Patient(models.Model):
    phone_number = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.phone_number

class Medicine(models.Model):
    name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, blank=True)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class PharmacyInventory(models.Model):
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='inventory')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='inventory')
    stock_quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('pharmacy', 'medicine')

    def __str__(self):
        return f"{self.pharmacy} - {self.medicine} ({self.stock_quantity})"

class PatientPurchase(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='purchases')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='purchases')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot unit price
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Purchase {self.id} by {self.patient}"

class PatientInteractionLog(models.Model):
    TYPE_CHOICES = [
        ('query', 'Query'),
        ('sms', 'SMS'),
    ]
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('sent', 'sent'),
        ('failed', 'failed'),
        ('resolved', 'resolved'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='interactions')
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE, related_name='interactions')
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, related_name='interactions', null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    message_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Interaction {self.id} ({self.type})"

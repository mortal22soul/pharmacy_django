from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random

from core.models import (
    Pharmacy, Patient, Medicine, PharmacyInventory,
    PatientPurchase, PatientInteractionLog
)

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with fake data for testing"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🌱 Seeding database..."))

        # Clear old data (optional)
        PatientPurchase.objects.all().delete()
        PatientInteractionLog.objects.all().delete()
        PharmacyInventory.objects.all().delete()
        Pharmacy.objects.all().delete()
        Patient.objects.all().delete()
        Medicine.objects.all().delete()

        # Pharmacies
        pharmacies = []
        for _ in range(5):
            ph = Pharmacy.objects.create(
                name=fake.company(),
                address=fake.address(),
                latitude=round(random.uniform(28.5, 28.8), 6),   # around Delhi
                longitude=round(random.uniform(77.0, 77.3), 6),
                phone_number=fake.phone_number(),
                is_active=True,
                created_at=timezone.now(),
            )
            pharmacies.append(ph)

        # Patients
        patients = []
        for _ in range(10):
            pt = Patient.objects.create(
                phone_number=fake.msisdn(),
                name=fake.name(),
                created_at=timezone.now(),
            )
            patients.append(pt)

        # Medicines
        medicines = []
        for med_name in ["Paracetamol", "Amoxicillin", "Ibuprofen", "Aspirin", "Cough Syrup"]:
            m = Medicine.objects.create(
                name=med_name,
                manufacturer=fake.company(),
                details=fake.text(max_nb_chars=50),
            )
            medicines.append(m)

        # Inventory
        inventories = []
        for ph in pharmacies:
            for med in medicines:
                inv = PharmacyInventory.objects.create(
                    pharmacy=ph,
                    medicine=med,
                    stock_quantity=random.randint(5, 100),
                    price=round(random.uniform(10, 200), 2),
                )
                inventories.append(inv)

        # Purchases
        for _ in range(20):
            patient = random.choice(patients)
            inv = random.choice(inventories)
            qty = random.randint(1, 3)
            if inv.stock_quantity >= qty:
                inv.stock_quantity -= qty
                inv.save()
                PatientPurchase.objects.create(
                    patient=patient,
                    pharmacy=inv.pharmacy,
                    medicine=inv.medicine,
                    quantity=qty,
                    price=inv.price,
                )

        # Interaction logs
        for _ in range(20):
            PatientInteractionLog.objects.create(
                patient=random.choice(patients),
                pharmacy=random.choice(pharmacies),
                medicine=random.choice(medicines) if random.random() > 0.3 else None,
                type=random.choice(["query", "sms"]),
                message_text=fake.sentence(),
                status=random.choice(["pending", "sent", "failed", "resolved"]),
            )

        self.stdout.write(self.style.SUCCESS("✅ Database seeded successfully!"))

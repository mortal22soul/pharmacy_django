## Database Schema Documentation

pharmacy

| id | name | address | latitude | longitude | phone_number | is_active | created_at | updated_at |
|----|------|---------|---------|----------|---------------|---------|-------------|-------------|

patient

| id | phone_number | name (optional) | created_at | updated_at |
|----|---------------|----------------|------------|------------|

medicine

| id | name | manufacturer | details | created_at | updated_at |
|----|------|--------------|---------|------------|------------|

pharmacy_inventory

| id | pharmacy_id | medicine_id | stock_quantity | price | created_at | updated_at |
|----|--------------|--------------|-----------------|-------|-------------|-------------|

patient_purchase

| id | patient_id | pharmacy_id | medicine_id | quantity | price | created_at |
|----|------------|--------------|--------------|----------|-------|  -------------|

patient_interaction_log

| id | patient_id | pharmacy_id | medicine_id | type (query/sms) | message_text | status | created_at |
|----|------------|--------------|--------------|------------------|--------------|--------|-------------|

## 📦 Tables & Relationships

### **pharmacy**

* `id` **PK**
* One pharmacy → can have many `pharmacy_inventory` entries.
* One pharmacy → can appear in many `patient_purchase` and `patient_interaction_log` records.

---

### **patient**

* `id` **PK**
* One patient → can make many `patient_purchase` entries.
* One patient → can have many `patient_interaction_log` entries.

---

### **medicine**

* `id` **PK**
* One medicine → can be stocked in many pharmacies via `pharmacy_inventory`.
* One medicine → can be purchased by many patients (`patient_purchase`).
* One medicine → can appear in many `patient_interaction_log` entries.

---

### **pharmacy\_inventory**

* `id` **PK**
* `pharmacy_id` **FK → pharmacy.id**
* `medicine_id` **FK → medicine.id**
* Relationship:

  * A **junction table** connecting **pharmacy** and **medicine**.
  * Each row = stock details for one medicine in one pharmacy.

---

### **patient\_purchase**

* `id` **PK**
* `patient_id` **FK → patient.id**
* `pharmacy_id` **FK → pharmacy.id**
* `medicine_id` **FK → medicine.id**
* Relationship:

  * Each row = purchase record linking **patient + pharmacy + medicine**.
  * Tracks quantity, price, and timestamp.

---

### **patient\_interaction\_log**

* `id` **PK**
* `patient_id` **FK → patient.id**
* `pharmacy_id` **FK → pharmacy.id**
* `medicine_id` **FK → medicine.id (nullable if query not about a specific medicine)**
* Relationship:

  * Each row = interaction (query or SMS) involving **patient + pharmacy (+ optional medicine)**.
  * Flexible: can log general inquiries or medicine-specific ones.

---

## 🔗 Relationship Summary (short form)

* **Pharmacy (1) → (∞) PharmacyInventory → (∞) Medicine**
* **Pharmacy (1) → (∞) PatientPurchase ← (∞) Patient**
* **Pharmacy (1) → (∞) PatientInteractionLog ← (∞) Patient**
* **Medicine (1) → (∞) PatientPurchase**
* **Medicine (1) → (∞) PatientInteractionLog**

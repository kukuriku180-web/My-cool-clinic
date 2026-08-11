# 🏥 Clinic Appointment System

A Python-based appointment management system for a medical clinic, using SQLite for persistent data storage.

**Submitted by:** [Noga Rosenberg]

## What Was Implemented

### Core Features (Required):

* ✅ Add new appointment (patient name, phone, date, time, doctor, service type)
* ✅ View all appointments
* ✅ View appointments by date
* ✅ Search appointments by patient name
* ✅ Update appointment status (pending / confirmed / completed / cancelled)
* ✅ Delete appointment with confirmation
* ✅ Basic conflict detection (warning if same doctor/date/time)
* ✅ Input validation (empty fields not allowed)
* ✅ Error handling with try/except throughout

### Bonus Features:

* ❌ Customer management and invoices (not implemented)
* ❌ Lead management (not implemented)

## How to Run

### Command-line version

1. Make sure Python 3 is installed
2. Open terminal in the project folder
3. Run:

```
python main.py
```

### GUI version

1. Make sure Python 3 is installed
2. Open terminal in the project folder
3. Run:

```
python clinic_appointments_GUI.py
```

The database file (`clinic.db`) will be created automatically on first run (shared by both versions).

## Project Structure

```
clinic_appointments/
├── main.py                      # Command-line menu and user interface
├── clinic_appointments_GUI.py   # Graphical (GUI) version of the app
├── database.py                  # All SQLite database functions
├── schema.sql                   # Database schema definition
└── README.md                    # This file
```

## Database Schema

See `schema.sql` for the full schema definition.
The `appointments` table includes:

* `id` - Auto-incremented unique ID
* `patient_name` - Patient's full name (required)
* `phone` - Patient's phone number
* `date` - Appointment date YYYY-MM-DD (required)
* `time` - Appointment time HH:MM (required)
* `doctor` - Doctor's name (required)
* `service_type` - Type of medical service (required)
* `reason` - Additional notes (optional)
* `status` - pending / confirmed / completed / cancelled

## Requirements

* Python 3.x
* SQLite3 (built into Python - no installation needed!)

from database import (
    create_table,
    add_appointment,
    view_all_appointments,
    view_appointments_by_date,
    update_status,
    delete_appointment,
    search_by_patient
)

SERVICES = [
    "General Checkup",
    "Blood Test",
    "X-Ray",
    "Consultation",
    "Follow-up",
    "Vaccination",
    "Other"
]

DOCTORS = [
    "Dr. Cohen",
    "Dr. Levi",
    "Dr. Mizrahi"
]

def print_menu():
    print("\n" + "="*40)
    print("   🏥 CLINIC APPOINTMENT SYSTEM")
    print("="*40)
    print("1. Add new appointment")
    print("2. View all appointments")
    print("3. View appointments by date")
    print("4. Search by patient name")
    print("5. Update appointment status")
    print("6. Delete appointment")
    print("7. Exit")
    print("="*40)

def handle_add_appointment():
    print("\n📝 NEW APPOINTMENT")
    print("-"*30)
    try:
        # Patient name
        while True:
            patient_name = input("Patient name: ").strip()
            if patient_name:
                break
            print("❌ Patient name cannot be empty!")

        # Phone
        phone = input("Phone number: ").strip()

        # Date
        while True:
            date = input("Appointment Date (YYYY-MM-DD, e.g. 2026-08-15): ").strip()
            if not date:
                print("❌ Date cannot be empty!")
                continue
            parts = date.split("-")
            if len(parts) == 3 and len(parts[0]) == 4:
                try:
                    int(parts[0]); int(parts[1]); int(parts[2])
                    if 1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= 31:
                        break
                except:
                    pass
            print("❌ Invalid date! Use YYYY-MM-DD (e.g. 2026-08-15)")

        # Time
        while True:
            time = input("Appointment Time (HH:MM, e.g. 09:00): ").strip()
            if not time:
                print("❌ Time cannot be empty!")
                continue
            parts = time.split(":")
            if len(parts) == 2:
                try:
                    h, m = int(parts[0]), int(parts[1])
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        break
                except:
                    pass
            print("❌ Invalid time! Use HH:MM (e.g. 09:00)")

        # Service type
        print("\nService types:")
        for i, service in enumerate(SERVICES, 1):
            print(f"{i}. {service}")
        while True:
            service_choice = input("Choose service (1-7): ").strip()
            if service_choice.isdigit() and 1 <= int(service_choice) <= len(SERVICES):
                service_type = SERVICES[int(service_choice) - 1]
                break
            print("❌ Invalid choice! Please try again.")

        # Doctor
        print("\nAvailable doctors:")
        for i, doctor in enumerate(DOCTORS, 1):
            print(f"{i}. {doctor}")
        while True:
            doctor_choice = input("Choose doctor (1-3): ").strip()
            if doctor_choice.isdigit() and 1 <= int(doctor_choice) <= len(DOCTORS):
                doctor = DOCTORS[int(doctor_choice) - 1]
                break
            print("❌ Invalid choice! Please try again.")

        # Reason
        reason = input("Additional notes (optional): ").strip()

        add_appointment(patient_name, phone, date, time, doctor, service_type, reason)

    except KeyboardInterrupt:
        print("\n❌ Cancelled.")

def handle_update_status():
    print("\n✏️ UPDATE STATUS")
    print("-"*30)
    try:
        view_all_appointments()
        appointment_id = int(input("\nEnter appointment ID to update: "))

        valid_statuses = ["pending", "confirmed", "completed", "cancelled"]

        while True:
            print("\nStatus options: pending / confirmed / completed / cancelled")
            new_status = input("Enter new status: ").strip().lower()
            if new_status in valid_statuses:
                update_status(appointment_id, new_status)
                break
            else:
                print(f"❌ '{new_status}' is not valid! Try again.")

    except ValueError:
        print("❌ Please enter a valid ID number!")
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")

def handle_delete_appointment():
    print("\n🗑️ DELETE APPOINTMENT")
    print("-"*30)
    try:
        view_all_appointments()
        appointment_id = int(input("\nEnter appointment ID to delete: "))
        confirm = input(f"Are you sure you want to delete appointment {appointment_id}? (yes/no): ").lower()
        if confirm == "yes":
            delete_appointment(appointment_id)
        else:
            print("❌ Deletion cancelled.")
    except ValueError:
        print("❌ Please enter a valid ID number!")
    except KeyboardInterrupt:
        print("\n❌ Cancelled.")

def handle_view_by_date():
    print("\n📅 VIEW BY DATE")
    print("-"*30)
    while True:
        date = input("Enter date (YYYY-MM-DD) or 'back' to return: ").strip()
        if date.lower() == "back":
            return
        parts = date.split("-")
        if len(parts) == 3 and len(parts[0]) == 4:
            try:
                int(parts[0]); int(parts[1]); int(parts[2])
                if 1 <= int(parts[1]) <= 12 and 1 <= int(parts[2]) <= 31:
                    view_appointments_by_date(date)
                    return
            except:
                pass
        print("❌ Invalid date! Use YYYY-MM-DD (e.g. 2026-08-15)")

def handle_search():
    print("\n🔍 SEARCH PATIENT")
    print("-"*30)
    while True:
        name = input("Enter patient name (or 'back' to return): ").strip()
        if name.lower() == "back":
            return
        if not name:
            print("❌ Please enter a name!")
            continue
        search_by_patient(name)
        another = input("\nSearch again? (yes/no): ").strip().lower()
        if another != "yes":
            return

def main():
    print("\n🏥 Welcome to the Clinic Appointment System!")
    create_table()

    while True:
        try:
            print_menu()
            choice = input("Choose an option (1-7): ").strip()

            if choice == "1":
                handle_add_appointment()
            elif choice == "2":
                view_all_appointments()
            elif choice == "3":
                handle_view_by_date()
            elif choice == "4":
                handle_search()
            elif choice == "5":
                handle_update_status()
            elif choice == "6":
                handle_delete_appointment()
            elif choice == "7":
                print("\n👋 Goodbye! Stay healthy!")
                break
            else:
                print("\n❌ Invalid option. Please choose 1-7.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Stay healthy!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

import sqlite3

DB_NAME = "clinic.db"

def create_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    """Create the appointments table if it doesn't exist (based on schema.sql)."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            phone TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            doctor TEXT NOT NULL,
            service_type TEXT NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    conn.commit()
    conn.close()

def add_appointment(patient_name, phone, date, time, doctor, service_type, reason=""):
    """Add a new appointment to the database."""
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Check for time conflict
        cursor.execute('''
            SELECT * FROM appointments 
            WHERE date = ? AND time = ? AND doctor = ? AND status != 'cancelled'
        ''', (date, time, doctor))
        existing = cursor.fetchone()
        if existing:
            print(f"\n⚠️ Warning: Dr. {doctor} already has an appointment at {date} {time}!")
            confirm = input("Add anyway? (yes/no): ").strip().lower()
            if confirm != "yes":
                conn.close()
                return

        cursor.execute('''
            INSERT INTO appointments (patient_name, phone, date, time, doctor, service_type, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (patient_name, phone, date, time, doctor, service_type, reason))
        conn.commit()
        conn.close()
        print(f"\n✅ Appointment added successfully for {patient_name}!")
    except Exception as e:
        print(f"\n❌ Error adding appointment: {e}")

def view_all_appointments():
    """View all appointments in the database."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments ORDER BY date, time')
        appointments = cursor.fetchall()
        conn.close()

        if not appointments:
            print("\n📋 No appointments found.")
            return

        print("\n" + "="*85)
        print(f"{'ID':<5} {'Patient':<20} {'Date':<12} {'Time':<8} {'Doctor':<15} {'Service':<15} {'Status':<10}")
        print("="*85)
        for apt in appointments:
            print(f"{apt['id']:<5} {apt['patient_name']:<20} {apt['date']:<12} {apt['time']:<8} {apt['doctor']:<15} {apt['service_type']:<15} {apt['status']:<10}")
        print("="*85)

    except Exception as e:
        print(f"\n❌ Error viewing appointments: {e}")

def view_appointments_by_date(date):
    """View all appointments for a specific date."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE date = ? ORDER BY time', (date,))
        appointments = cursor.fetchall()
        conn.close()

        if not appointments:
            print(f"\n📋 No appointments found for {date}.")
            return

        print(f"\n📅 Appointments for {date}:")
        print("="*70)
        for apt in appointments:
            print(f"ID: {apt['id']} | {apt['time']} | {apt['patient_name']} | {apt['service_type']} | {apt['doctor']} | {apt['status']}")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error viewing appointments: {e}")

def update_status(appointment_id, new_status):
    """Update the status of an appointment."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (new_status, appointment_id))

        if cursor.rowcount == 0:
            print(f"\n❌ No appointment found with ID {appointment_id}.")
        else:
            print(f"\n✅ Appointment {appointment_id} status updated to '{new_status}'!")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"\n❌ Error updating appointment: {e}")

def delete_appointment(appointment_id):
    """Delete an appointment by ID."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))

        if cursor.rowcount == 0:
            print(f"\n❌ No appointment found with ID {appointment_id}.")
        else:
            print(f"\n✅ Appointment {appointment_id} deleted successfully!")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"\n❌ Error deleting appointment: {e}")

def search_by_patient(patient_name):
    """Search appointments by patient name."""
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM appointments WHERE patient_name LIKE ? ORDER BY date, time',
                      (f'%{patient_name}%',))
        appointments = cursor.fetchall()
        conn.close()

        if not appointments:
            print(f"\n📋 No appointments found for patient '{patient_name}'.")
            return

        print(f"\n🔍 Results for '{patient_name}':")
        print("="*70)
        for apt in appointments:
            print(f"ID: {apt['id']} | {apt['date']} {apt['time']} | {apt['service_type']} | {apt['doctor']} | {apt['status']}")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error searching: {e}")

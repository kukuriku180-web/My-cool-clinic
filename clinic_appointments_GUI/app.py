import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "clinic.db"

SERVICES = [
    "General Checkup",
    "Blood Test",
    "X-Ray",
    "Consultation",
    "Follow-up",
    "Vaccination",
    "Other"
]

DOCTORS = ["Dr. Cohen", "Dr. Levi", "Dr. Mizrahi"]

COLORS = {
    "bg": "#1a1a2e",
    "sidebar": "#16213e",
    "card": "#0f3460",
    "accent": "#e94560",
    "accent2": "#533483",
    "text": "#ffffff",
    "text_dim": "#a0a0b0",
    "success": "#00b894",
    "warning": "#fdcb6e",
    "error": "#d63031",
    "input_bg": "#1e2a3a",
    "table_odd": "#0f3460",
    "table_even": "#16213e",
    "hover": "#e94560",
}

STATUS_COLORS = {
    "pending": "#fdcb6e",
    "confirmed": "#00b894",
    "completed": "#74b9ff",
    "cancelled": "#d63031",
}

# ==================== DATABASE ====================

def create_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
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

def db_add_appointment(patient_name, phone, date, time, doctor, service_type, reason=""):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO appointments (patient_name, phone, date, time, doctor, service_type, reason, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (patient_name, phone, date, time, doctor, service_type, reason))
    conn.commit()
    conn.close()

def db_get_all():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM appointments ORDER BY date, time')
    rows = cursor.fetchall()
    conn.close()
    return rows

def db_search(query):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM appointments 
        WHERE patient_name LIKE ? OR doctor LIKE ? OR service_type LIKE ? OR status LIKE ?
        ORDER BY date, time
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    return rows

def db_update_status(apt_id, new_status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE appointments SET status = ? WHERE id = ?', (new_status, apt_id))
    conn.commit()
    conn.close()

def db_delete(apt_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM appointments WHERE id = ?', (apt_id,))
    conn.commit()
    conn.close()

def db_get_stats():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM appointments')
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'confirmed'")
    confirmed = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    conn.close()
    return total, pending, confirmed, completed

# ==================== GUI ====================

class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏥 Clinic Appointment System")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        self.selected_id = None
        self.current_page = "dashboard"

        self._build_layout()
        self.show_dashboard()

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar"], width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        tk.Label(self.sidebar, text="🏥", font=("Arial", 32), bg=COLORS["sidebar"], fg=COLORS["accent"]).pack(pady=(20, 5))
        tk.Label(self.sidebar, text="Clinic System", font=("Arial", 13, "bold"), bg=COLORS["sidebar"], fg=COLORS["text"]).pack()
        tk.Label(self.sidebar, text="─" * 20, bg=COLORS["sidebar"], fg=COLORS["text_dim"]).pack(pady=10)

        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("➕", "Add Appointment", "add"),
            ("📋", "All Appointments", "list"),
            ("🔍", "Search", "search"),
        ]

        for icon, label, page in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=f"  {icon}  {label}",
                font=("Arial", 11),
                bg=COLORS["sidebar"],
                fg=COLORS["text"],
                activebackground=COLORS["accent"],
                activeforeground=COLORS["text"],
                relief="flat",
                anchor="w",
                padx=15,
                pady=10,
                cursor="hand2",
                command=lambda p=page: self.navigate(p)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page] = btn

        # Main content
        self.main = tk.Frame(self.root, bg=COLORS["bg"])
        self.main.pack(side="left", fill="both", expand=True)

        # Header
        self.header = tk.Frame(self.main, bg=COLORS["bg"], height=60)
        self.header.pack(fill="x", padx=20, pady=(15, 0))

        self.page_title = tk.Label(self.header, text="Dashboard", font=("Arial", 20, "bold"), bg=COLORS["bg"], fg=COLORS["text"])
        self.page_title.pack(side="left")

        # Content area
        self.content = tk.Frame(self.main, bg=COLORS["bg"])
        self.content.pack(fill="both", expand=True, padx=20, pady=10)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def navigate(self, page):
        for p, btn in self.nav_buttons.items():
            btn.configure(bg=COLORS["sidebar"] if p != page else COLORS["accent"])
        self.current_page = page
        if page == "dashboard":
            self.show_dashboard()
        elif page == "add":
            self.show_add()
        elif page == "list":
            self.show_list()
        elif page == "search":
            self.show_search()

    def make_card(self, parent, **kwargs):
        card = tk.Frame(parent, bg=COLORS["card"], **kwargs)
        return card

    # ==================== DASHBOARD ====================
    def show_dashboard(self):
        self.clear_content()
        self.page_title.configure(text="📊 Dashboard")

        total, pending, confirmed, completed = db_get_stats()

        # Stats cards
        stats_frame = tk.Frame(self.content, bg=COLORS["bg"])
        stats_frame.pack(fill="x", pady=(0, 20))

        stats = [
            ("Total Appointments", total, "📋", COLORS["accent2"]),
            ("Pending", pending, "⏳", COLORS["warning"]),
            ("Confirmed", confirmed, "✅", COLORS["success"]),
            ("Completed", completed, "🏁", "#74b9ff"),
        ]

        for i, (label, value, icon, color) in enumerate(stats):
            card = tk.Frame(stats_frame, bg=color, padx=20, pady=15)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            stats_frame.columnconfigure(i, weight=1)

            tk.Label(card, text=icon, font=("Arial", 24), bg=color, fg="white").pack()
            tk.Label(card, text=str(value), font=("Arial", 28, "bold"), bg=color, fg="white").pack()
            tk.Label(card, text=label, font=("Arial", 10), bg=color, fg="white").pack()

        # Recent appointments
        tk.Label(self.content, text="Recent Appointments", font=("Arial", 14, "bold"),
                bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(10, 5))

        self._build_table(self.content, db_get_all()[:5], show_actions=False)

    # ==================== ADD APPOINTMENT ====================
    def show_add(self):
        self.clear_content()
        self.page_title.configure(text="➕ Add New Appointment")

        card = self.make_card(self.content, padx=30, pady=25)
        card.pack(fill="both", expand=True)

        self.entries = {}

        fields = [
            ("Patient Name *", "patient_name", "entry"),
            ("Phone Number", "phone", "entry"),
            ("Appointment Date (YYYY-MM-DD) *", "date", "entry"),
            ("Time (HH:MM) *", "time", "entry"),
            ("Service Type *", "service_type", "combo_service"),
            ("Doctor *", "doctor", "combo_doctor"),
            ("Additional Notes", "reason", "entry"),
        ]

        for i, (label, key, field_type) in enumerate(fields):
            row = i // 2
            col = (i % 2) * 2

            tk.Label(card, text=label, font=("Arial", 10), bg=COLORS["card"],
                    fg=COLORS["text_dim"]).grid(row=row*2, column=col, sticky="w", pady=(10, 2), padx=10)

            if field_type == "entry":
                entry = tk.Entry(card, font=("Arial", 11), bg=COLORS["input_bg"],
                               fg=COLORS["text"], insertbackground=COLORS["text"],
                               relief="flat", width=25)
                entry.grid(row=row*2+1, column=col, sticky="ew", padx=10, pady=(0, 5), ipady=8)
                self.entries[key] = entry

            elif field_type == "combo_service":
                combo = ttk.Combobox(card, values=SERVICES, font=("Arial", 11), width=23, state="readonly")
                combo.set(SERVICES[0])
                combo.grid(row=row*2+1, column=col, sticky="ew", padx=10, pady=(0, 5))
                self.entries[key] = combo

            elif field_type == "combo_doctor":
                combo = ttk.Combobox(card, values=DOCTORS, font=("Arial", 11), width=23, state="readonly")
                combo.set(DOCTORS[0])
                combo.grid(row=row*2+1, column=col, sticky="ew", padx=10, pady=(0, 5))
                self.entries[key] = combo

        for i in range(4):
            card.columnconfigure(i, weight=1)

        # Buttons
        btn_frame = tk.Frame(card, bg=COLORS["card"])
        btn_frame.grid(row=20, column=0, columnspan=4, pady=20)

        tk.Button(btn_frame, text="✅  Save Appointment", font=("Arial", 12, "bold"),
                 bg=COLORS["success"], fg="white", relief="flat", padx=20, pady=10,
                 cursor="hand2", command=self.save_appointment).pack(side="left", padx=10)

        tk.Button(btn_frame, text="🗑️  Clear", font=("Arial", 12),
                 bg=COLORS["text_dim"], fg="white", relief="flat", padx=20, pady=10,
                 cursor="hand2", command=self.clear_form).pack(side="left", padx=10)

    def clear_form(self):
        for key, widget in self.entries.items():
            if isinstance(widget, ttk.Combobox):
                widget.set(SERVICES[0] if key == "service_type" else DOCTORS[0])
            else:
                widget.delete(0, "end")

    def save_appointment(self):
        patient_name = self.entries["patient_name"].get().strip()
        phone = self.entries["phone"].get().strip()
        date = self.entries["date"].get().strip()
        time = self.entries["time"].get().strip()
        service_type = self.entries["service_type"].get()
        doctor = self.entries["doctor"].get()
        reason = self.entries["reason"].get().strip()

        # Validation
        if not patient_name:
            messagebox.showerror("Error", "Patient name is required!")
            return
        if not date:
            messagebox.showerror("Error", "Date is required!")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format! Use YYYY-MM-DD")
            return
        if not time:
            messagebox.showerror("Error", "Time is required!")
            return
        try:
            datetime.strptime(time, "%H:%M")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format! Use HH:MM")
            return

        db_add_appointment(patient_name, phone, date, time, doctor, service_type, reason)
        messagebox.showinfo("Success", f"✅ Appointment added for {patient_name}!")
        self.clear_form()
        self.navigate("list")

    # ==================== LIST ====================
    def show_list(self):
        self.clear_content()
        self.page_title.configure(text="📋 All Appointments")

        # Top bar
        top = tk.Frame(self.content, bg=COLORS["bg"])
        top.pack(fill="x", pady=(0, 10))

        tk.Button(top, text="🔄 Refresh", font=("Arial", 10),
                 bg=COLORS["accent2"], fg="white", relief="flat", padx=10, pady=5,
                 cursor="hand2", command=self.show_list).pack(side="left")

        rows = db_get_all()
        tk.Label(top, text=f"{len(rows)} appointments", font=("Arial", 10),
                bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="right")

        self._build_table(self.content, rows, show_actions=True)

    def _build_table(self, parent, rows, show_actions=True):
        # Table frame with scrollbar
        table_frame = tk.Frame(parent, bg=COLORS["card"])
        table_frame.pack(fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")

        # Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background=COLORS["card"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["card"],
                        rowheight=35,
                        font=("Arial", 10))
        style.configure("Custom.Treeview.Heading",
                        background=COLORS["accent"],
                        foreground="white",
                        font=("Arial", 10, "bold"))
        style.map("Custom.Treeview",
                 background=[("selected", COLORS["accent2"])])

        cols = ("ID", "Patient", "Phone", "Date", "Time", "Doctor", "Service", "Status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings",
                                  style="Custom.Treeview",
                                  yscrollcommand=vsb.set,
                                  xscrollcommand=hsb.set)

        col_widths = [50, 150, 120, 100, 70, 120, 130, 100]
        for col, width in zip(cols, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)

        # Insert rows
        for i, row in enumerate(rows):
            status = row["status"] if row["status"] else "pending"
            tag = f"status_{status}"
            self.tree.insert("", "end", iid=row["id"],
                            values=(row["id"], row["patient_name"], row["phone"] or "",
                                   row["date"], row["time"], row["doctor"],
                                   row["service_type"], status.upper()),
                            tags=(tag,))
            color = STATUS_COLORS.get(status, COLORS["text"])
            self.tree.tag_configure(tag, foreground=color)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        if show_actions:
            self.tree.bind("<ButtonRelease-1>", self.on_select)
            self._build_actions(parent)

    def _build_actions(self, parent):
        action_frame = tk.Frame(parent, bg=COLORS["bg"])
        action_frame.pack(fill="x", pady=10)

        tk.Label(action_frame, text="Update Status:", font=("Arial", 10),
                bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="left", padx=(0, 5))

        self.status_var = tk.StringVar(value="confirmed")
        for status in ["pending", "confirmed", "completed", "cancelled"]:
            color = STATUS_COLORS.get(status, "white")
            tk.Radiobutton(action_frame, text=status.capitalize(),
                          variable=self.status_var, value=status,
                          bg=COLORS["bg"], fg=color,
                          selectcolor=COLORS["card"],
                          activebackground=COLORS["bg"],
                          font=("Arial", 10)).pack(side="left", padx=5)

        tk.Button(action_frame, text="✏️ Update", font=("Arial", 10),
                 bg=COLORS["warning"], fg="black", relief="flat", padx=10, pady=5,
                 cursor="hand2", command=self.update_status).pack(side="left", padx=10)

        tk.Button(action_frame, text="🗑️ Delete", font=("Arial", 10),
                 bg=COLORS["error"], fg="white", relief="flat", padx=10, pady=5,
                 cursor="hand2", command=self.delete_appointment).pack(side="left", padx=5)

        self.selected_label = tk.Label(action_frame, text="No appointment selected",
                                        font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["text_dim"])
        self.selected_label.pack(side="right")

    def on_select(self, event):
        selection = self.tree.selection()
        if selection:
            self.selected_id = int(selection[0])
            item = self.tree.item(selection[0])
            patient = item["values"][1]
            self.selected_label.configure(text=f"Selected: {patient} (ID: {self.selected_id})",
                                          fg=COLORS["success"])

    def update_status(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select an appointment first!")
            return
        new_status = self.status_var.get()
        db_update_status(self.selected_id, new_status)
        messagebox.showinfo("Success", f"✅ Status updated to '{new_status}'!")
        self.selected_id = None
        self.show_list()

    def delete_appointment(self):
        if not self.selected_id:
            messagebox.showwarning("Warning", "Please select an appointment first!")
            return
        confirm = messagebox.askyesno("Confirm", f"Delete appointment ID {self.selected_id}?")
        if confirm:
            db_delete(self.selected_id)
            messagebox.showinfo("Success", "✅ Appointment deleted!")
            self.selected_id = None
            self.show_list()

    # ==================== SEARCH ====================
    def show_search(self):
        self.clear_content()
        self.page_title.configure(text="🔍 Search Appointments")

        # Search bar
        search_frame = tk.Frame(self.content, bg=COLORS["bg"])
        search_frame.pack(fill="x", pady=(0, 15))

        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.do_search())

        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=("Arial", 13), bg=COLORS["input_bg"],
                               fg=COLORS["text"], insertbackground=COLORS["text"],
                               relief="flat", width=40)
        search_entry.pack(side="left", ipady=10, padx=(0, 10))
        search_entry.insert(0, "Search by name, doctor, service or status...")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, "end") if search_entry.get().startswith("Search") else None)
        search_entry.focus()

        tk.Button(search_frame, text="🔍 Search", font=("Arial", 12),
                 bg=COLORS["accent"], fg="white", relief="flat", padx=15, pady=8,
                 cursor="hand2", command=self.do_search).pack(side="left")

        # Results
        self.search_results_frame = tk.Frame(self.content, bg=COLORS["bg"])
        self.search_results_frame.pack(fill="both", expand=True)

        self._show_search_results(db_get_all())

    def do_search(self):
        query = self.search_var.get().strip()
        if query and not query.startswith("Search"):
            rows = db_search(query)
        else:
            rows = db_get_all()
        self._show_search_results(rows)

    def _show_search_results(self, rows):
        for w in self.search_results_frame.winfo_children():
            w.destroy()

        tk.Label(self.search_results_frame, text=f"{len(rows)} results found",
                font=("Arial", 10), bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(anchor="w", pady=(0, 5))

        self._build_table(self.search_results_frame, rows, show_actions=False)


# ==================== MAIN ====================
if __name__ == "__main__":
    create_table()
    root = tk.Tk()
    app = ClinicApp(root)
    root.mainloop()

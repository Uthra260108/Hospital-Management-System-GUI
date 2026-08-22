import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# Database connection setup
def setup_database():
    passwd = input("Enter the MySQL root password: ")

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd=passwd
        )
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS my_hospital")
        cursor.execute("USE my_hospital")
        return db, cursor

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise SystemExit(1)


# Create required tables
def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) NOT NULL,
            sex VARCHAR(10) NOT NULL,
            age INT,
            address VARCHAR(50),
            contactnumber VARCHAR(30)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(30) NOT NULL,
            specialisation VARCHAR(40),
            age INT,
            address VARCHAR(50),
            contact VARCHAR(30),
            fees INT,
            monthly_salary INT
        )
    """)

    # Added TIME because the appointment form uses a time field.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_name VARCHAR(30),
            doctor_name VARCHAR(30),
            appointment_date DATE,
            time TIME,
            status VARCHAR(20)
        )
    """)

    # Added status because the billing form stores Paid/Unpaid.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billing_details(
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_name VARCHAR(30),
            amount INT,
            status VARCHAR(20),
            date DATE
        )
    """)


class HospitalManagementSystem:
    def __init__(self, root, db, cursor):
        self.root = root
        self.db = db
        self.cursor = cursor

        self.root.title("Hospital Management System")
        self.root.geometry("900x700")

        self.admin_dashboard()

    def admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Admin Dashboard",
            font=("Arial", 24)
        ).pack(pady=20)

        tk.Button(
            self.root,
            text="Manage Patients",
            font=("Arial", 14),
            command=self.manage_patients
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Manage Doctors",
            font=("Arial", 14),
            command=self.manage_doctors
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Manage Appointments",
            font=("Arial", 14),
            command=self.manage_appointments
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Manage Billing",
            font=("Arial", 14),
            command=self.manage_billings
        ).pack(pady=10)

        tk.Button(
            self.root,
            text="Logout",
            font=("Arial", 14),
            command=self.root.destroy
        ).pack(pady=20)

    # Manage Patients
    def manage_patients(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Manage Patients",
            font=("Arial", 24)
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        columns = (
            "ID", "Name", "Sex", "Age",
            "Address", "Contact Number"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_patients():
            tree.delete(*tree.get_children())
            self.cursor.execute("SELECT * FROM patient_details")
            rows = self.cursor.fetchall()

            for row in rows:
                tree.insert("", tk.END, values=row)

        load_patients()

        def add_patient():
            def save_patient():
                name = name_entry.get()
                sex = sex_var.get()
                age = age_entry.get()
                address = address_entry.get()
                contact = contact_entry.get()

                try:
                    self.cursor.execute(
                        """
                        INSERT INTO patient_details
                        (name, sex, age, address, contactnumber)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (name, sex, age, address, contact)
                    )

                    self.db.commit()
                    messagebox.showinfo(
                        "Success",
                        "Patient added successfully"
                    )
                    add_window.destroy()
                    load_patients()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error adding patient: {e}"
                    )

            add_window = tk.Toplevel(self.root)
            add_window.title("Add Patient")
            add_window.geometry("400x400")

            tk.Label(add_window, text="Name").pack(pady=5)
            name_entry = tk.Entry(add_window)
            name_entry.pack()

            tk.Label(add_window, text="Sex").pack(pady=5)
            sex_var = tk.StringVar()

            tk.Radiobutton(
                add_window,
                text="Male",
                variable=sex_var,
                value="Male"
            ).pack()

            tk.Radiobutton(
                add_window,
                text="Female",
                variable=sex_var,
                value="Female"
            ).pack()

            tk.Label(add_window, text="Age").pack(pady=5)
            age_entry = tk.Entry(add_window)
            age_entry.pack()

            tk.Label(add_window, text="Address").pack(pady=5)
            address_entry = tk.Entry(add_window)
            address_entry.pack()

            tk.Label(add_window, text="Contact Number").pack(pady=5)
            contact_entry = tk.Entry(add_window)
            contact_entry.pack()

            tk.Button(
                add_window,
                text="Save",
                command=save_patient
            ).pack(pady=20)

        def delete_patient():
            selected = tree.selection()

            if selected:
                patient_id = tree.item(
                    selected[0],
                    "values"
                )[0]

                try:
                    self.cursor.execute(
                        "DELETE FROM patient_details WHERE id = %s",
                        (patient_id,)
                    )
                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Patient deleted successfully"
                    )
                    load_patients()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error deleting patient: {e}"
                    )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Please select a patient to delete"
                )

        tk.Button(
            self.root,
            text="Add Patient",
            font=("Arial", 14),
            command=add_patient
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Delete Patient",
            font=("Arial", 14),
            command=delete_patient
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 14),
            command=self.admin_dashboard
        ).pack(pady=20)

    # Manage Doctors
    def manage_doctors(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Manage Doctors",
            font=("Arial", 24)
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        columns = (
            "ID", "Name", "Specialization", "Contact Number"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_doctors():
            tree.delete(*tree.get_children())
            self.cursor.execute("SELECT * FROM doctor_details")
            rows = self.cursor.fetchall()

            # The Treeview displays selected fields from each database row.
            for row in rows:
                tree.insert(
                    "",
                    tk.END,
                    values=(row[0], row[1], row[2], row[5])
                )

        load_doctors()

        def add_doctor():
            def save_doctor():
                name = name_entry.get()
                specialization = specialization_entry.get()
                contact = contact_entry.get()

                try:
                    self.cursor.execute(
                        """
                        INSERT INTO doctor_details
                        (name, specialisation, contact)
                        VALUES (%s, %s, %s)
                        """,
                        (name, specialization, contact)
                    )

                    self.db.commit()
                    messagebox.showinfo(
                        "Success",
                        "Doctor added successfully"
                    )
                    add_window.destroy()
                    load_doctors()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error adding doctor: {e}"
                    )

            add_window = tk.Toplevel(self.root)
            add_window.title("Add Doctor")
            add_window.geometry("400x400")

            tk.Label(add_window, text="Name").pack(pady=5)
            name_entry = tk.Entry(add_window)
            name_entry.pack()

            tk.Label(
                add_window,
                text="Specialization"
            ).pack(pady=5)

            specialization_entry = tk.Entry(add_window)
            specialization_entry.pack()

            tk.Label(
                add_window,
                text="Contact Number"
            ).pack(pady=5)

            contact_entry = tk.Entry(add_window)
            contact_entry.pack()

            tk.Button(
                add_window,
                text="Save",
                command=save_doctor
            ).pack(pady=20)

        def delete_doctor():
            selected = tree.selection()

            if selected:
                doctor_id = tree.item(
                    selected[0],
                    "values"
                )[0]

                try:
                    self.cursor.execute(
                        "DELETE FROM doctor_details WHERE id = %s",
                        (doctor_id,)
                    )
                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Doctor deleted successfully"
                    )
                    load_doctors()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error deleting doctor: {e}"
                    )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Please select a doctor to delete"
                )

        tk.Button(
            self.root,
            text="Add Doctor",
            font=("Arial", 14),
            command=add_doctor
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Delete Doctor",
            font=("Arial", 14),
            command=delete_doctor
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 14),
            command=self.admin_dashboard
        ).pack(pady=20)

    # Manage Appointments
    def manage_appointments(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Manage Appointments",
            font=("Arial", 24)
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        columns = (
            "ID", "Patient Name", "Doctor Name",
            "Date", "Time", "Status"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_appointments():
            tree.delete(*tree.get_children())
            self.cursor.execute("SELECT * FROM appointment_details")
            rows = self.cursor.fetchall()

            for row in rows:
                tree.insert("", tk.END, values=row)

        load_appointments()

        def add_appointment():
            def save_appointment():
                patient_name = patient_name_entry.get()
                doctor_name = doctor_name_entry.get()
                appointment_date = date_entry.get()
                appointment_time = time_entry.get()

                try:
                    self.cursor.execute(
                        """
                        INSERT INTO appointment_details
                        (patient_name, doctor_name, appointment_date, time)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            patient_name,
                            doctor_name,
                            appointment_date,
                            appointment_time
                        )
                    )

                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Appointment added successfully"
                    )
                    add_window.destroy()
                    load_appointments()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error adding appointment: {e}"
                    )

            add_window = tk.Toplevel(self.root)
            add_window.title("Add Appointment")
            add_window.geometry("400x400")

            tk.Label(
                add_window,
                text="Patient Name"
            ).pack(pady=5)

            patient_name_entry = tk.Entry(add_window)
            patient_name_entry.pack()

            tk.Label(
                add_window,
                text="Doctor Name"
            ).pack(pady=5)

            doctor_name_entry = tk.Entry(add_window)
            doctor_name_entry.pack()

            tk.Label(
                add_window,
                text="Date (YYYY-MM-DD)"
            ).pack(pady=5)

            date_entry = tk.Entry(add_window)
            date_entry.pack()

            tk.Label(
                add_window,
                text="Time (HH:MM)"
            ).pack(pady=5)

            time_entry = tk.Entry(add_window)
            time_entry.pack()

            tk.Button(
                add_window,
                text="Save",
                command=save_appointment
            ).pack(pady=20)

        def delete_appointment():
            selected = tree.selection()

            if selected:
                appointment_id = tree.item(
                    selected[0],
                    "values"
                )[0]

                try:
                    self.cursor.execute(
                        "DELETE FROM appointment_details WHERE id = %s",
                        (appointment_id,)
                    )
                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Appointment deleted successfully"
                    )
                    load_appointments()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error deleting appointment: {e}"
                    )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Please select an appointment to delete"
                )

        tk.Button(
            self.root,
            text="Add Appointment",
            font=("Arial", 14),
            command=add_appointment
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Delete Appointment",
            font=("Arial", 14),
            command=delete_appointment
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 14),
            command=self.admin_dashboard
        ).pack(pady=20)

    # Manage Billing
    def manage_billings(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(
            self.root,
            text="Manage Billings",
            font=("Arial", 24)
        ).pack(pady=20)

        frame = tk.Frame(self.root)
        frame.pack()

        columns = (
            "ID", "Patient Name", "Amount",
            "Status", "Payment Date"
        )

        tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            height=15
        )
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL,
            command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def load_billings():
            tree.delete(*tree.get_children())
            self.cursor.execute("SELECT * FROM billing_details")
            rows = self.cursor.fetchall()

            for row in rows:
                tree.insert("", tk.END, values=row)

        load_billings()

        def add_billing():
            def save_billing():
                patient_name = patient_name_entry.get()
                amount = amount_entry.get()
                status = status_var.get()
                payment_date = payment_date_entry.get()

                try:
                    self.cursor.execute(
                        """
                        INSERT INTO billing_details
                        (patient_name, amount, status, date)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (
                            patient_name,
                            amount,
                            status,
                            payment_date
                        )
                    )

                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Billing added successfully"
                    )
                    add_window.destroy()
                    load_billings()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error adding billing: {e}"
                    )

            add_window = tk.Toplevel(self.root)
            add_window.title("Add Billing")
            add_window.geometry("400x400")

            tk.Label(
                add_window,
                text="Patient Name"
            ).pack(pady=5)

            patient_name_entry = tk.Entry(add_window)
            patient_name_entry.pack()

            tk.Label(
                add_window,
                text="Amount"
            ).pack(pady=5)

            amount_entry = tk.Entry(add_window)
            amount_entry.pack()

            tk.Label(
                add_window,
                text="Status"
            ).pack(pady=5)

            status_var = tk.StringVar()

            tk.Radiobutton(
                add_window,
                text="Paid",
                variable=status_var,
                value="Paid"
            ).pack()

            tk.Radiobutton(
                add_window,
                text="Unpaid",
                variable=status_var,
                value="Unpaid"
            ).pack()

            tk.Label(
                add_window,
                text="Payment Date (YYYY-MM-DD)"
            ).pack(pady=5)

            payment_date_entry = tk.Entry(add_window)
            payment_date_entry.pack()

            tk.Button(
                add_window,
                text="Save",
                command=save_billing
            ).pack(pady=20)

        def delete_billing():
            selected = tree.selection()

            if selected:
                billing_id = tree.item(
                    selected[0],
                    "values"
                )[0]

                try:
                    self.cursor.execute(
                        "DELETE FROM billing_details WHERE id = %s",
                        (billing_id,)
                    )
                    self.db.commit()

                    messagebox.showinfo(
                        "Success",
                        "Billing deleted successfully"
                    )
                    load_billings()

                except Exception as e:
                    messagebox.showerror(
                        "Error",
                        f"Error deleting billing: {e}"
                    )
            else:
                messagebox.showwarning(
                    "Warning",
                    "Please select a billing to delete"
                )

        tk.Button(
            self.root,
            text="Add Billing",
            font=("Arial", 14),
            command=add_billing
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Delete Billing",
            font=("Arial", 14),
            command=delete_billing
        ).pack(pady=5)

        tk.Button(
            self.root,
            text="Back",
            font=("Arial", 14),
            command=self.admin_dashboard
        ).pack(pady=20)


if __name__ == "__main__":
    db, cursor = setup_database()
    create_tables(cursor)

    root = tk.Tk()
    app = HospitalManagementSystem(root, db, cursor)
    root.mainloop()

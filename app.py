import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import bcrypt
import shutil
import csv
import re
import os
from tkinter import filedialog

class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Login")
        self.geometry("300x300")

        self.bind("<Return>", lambda event=None: self.check_credentials())

        self.username_label = ttk.Label(self, text="Username:")
        self.username_label.pack(pady=10)

        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.pack(pady=10)

        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        self.login_button = ttk.Button(self, text="Login", command=self.check_credentials)
        self.login_button.pack(pady=20)


        self.forgot_password_button = ttk.Button(self, text="Forgot Password?", command=self.forgot_password_alert)
        self.forgot_password_button.pack(pady=10)

    def forgot_password_alert(self):
        messagebox.showinfo("Forgot Password", "Please contact the administration for password recovery.")


    def check_credentials(self):
        """Check if entered credentials match any in the database."""
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password, access_level FROM staff WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user[0]):  
            self.parent.access_level = user[1]
            self.destroy()
            self.parent.setup_interface()
            self.parent.deiconify()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

class MainPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.appointments_button = ttk.Button(self, text="Appointments", command=self.open_appointments)
        self.appointments_button.pack(pady=20)

        self.clients_button = ttk.Button(self, text="Clients", command=self.open_clients)
        self.clients_button.pack(pady=20)

        self.staff_button = ttk.Button(self, text="Staff", command=self.open_staff)
        self.staff_button.pack(pady=20)

        self.inventory_button = ttk.Button(self, text="Inventory", command=self.open_inventory)
        self.inventory_button.pack(pady=20)

        self.logout_button = ttk.Button(self, text="Logout", command=self.logout)
        self.logout_button.pack(pady=20)

    def open_appointments(self):
        self.clear_frame()
        AppointmentsPage(self)

    def open_clients(self):
        self.clear_frame()
        ClientsPage(self)

    def open_staff(self):
        self.clear_frame()
        StaffPage(self)

    def open_inventory(self):
        self.clear_frame()
        InventoryPage(self)

    def logout(self):
        self.clear_frame()
        self.parent.withdraw()
        login = LoginWindow(self.parent)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class DataOptionsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Data Options")
        self.geometry("300x200")

        ttk.Button(self, text="Backup Database", command=parent.backup_database).pack(pady=20)
        ttk.Button(self, text="Restore Database", command=self.restore_database).pack(pady=20)
        ttk.Button(self, text="Export All Clients", command=parent.export_all_clients).pack(pady=20)

    def restore_database(self):
        file_path = filedialog.askopenfilename(title="Select backup to restore", filetypes=[("Database Files", "*.db")])
        if not file_path:
            return
        try:
            shutil.copy2(file_path, 'physiotherapy.db')
            messagebox.showinfo("Success", "Database restored!")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")

class AppointmentsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Create the Treeview to show appointments
        columns = ("Client", "Staff", "Time", "Date", "Status")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        self.tree.column("Client", width=100)
        self.tree.column("Staff", width=100)
        self.tree.column("Time", width=50)
        self.tree.column("Date", width=70)
        self.tree.column("Status", width=80)

        # Load data into the treeview
        self.load_appointments()

        # Buttons for adding, editing, and deleting appointments
        self.add_button = ttk.Button(self, text="Add Appointment", command=self.open_add_appointment_window)
        self.add_button.pack(pady=10)

        self.edit_button = ttk.Button(self, text="Edit Appointment", command=self.open_edit_appointment_window)
        self.edit_button.pack(pady=10)

        self.delete_button = ttk.Button(self, text="Delete Appointment", command=self.delete_appointment)
        self.delete_button.pack(pady=10)

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.pack(pady=20)

    def load_appointments(self):
        # Remove existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT c.forename || ' ' || c.surname, s.forename || ' ' || s.surname, a.session_time, a.session_date, a.status \
                        FROM appointments a \
                        INNER JOIN clients c ON a.client_id = c.id \
                        INNER JOIN staff s ON a.staff_id = s.id")
        appointments = cursor.fetchall()

        for appointment in appointments:
            self.tree.insert("", "end", values=appointment)
        
        conn.close()

    def open_add_appointment_window(self):
        AddAppointmentWindow(self)

    def open_edit_appointment_window(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment to edit!")
            return

        # Fetch the ID of the appointment using a modified version of your previous SQL
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        appointment_data = self.tree.item(selected_item)
        client_name = appointment_data["values"][0]
        staff_name = appointment_data["values"][1]
        time = appointment_data["values"][2]
        date = appointment_data["values"][3]
        cursor.execute("SELECT a.id FROM appointments a WHERE client_id=(SELECT id FROM clients WHERE forename || ' ' || surname = ?) AND staff_id=(SELECT id FROM staff WHERE forename || ' ' || surname = ?) AND session_time=? AND session_date=?", (client_name, staff_name, time, date))
        appointment_id = cursor.fetchone()[0]
        conn.close()

        EditAppointmentWindow(self, appointment_id)

    def delete_appointment(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select an appointment to delete!")
            return

        response = messagebox.askyesno("Confirmation", "Are you sure you want to delete this appointment?")
        if not response:
            return

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        # Retrieve the ID from the selected appointment
        appointment_data = self.tree.item(selected_item)
        client_name = appointment_data["values"][0]
        staff_name = appointment_data["values"][1]
        time = appointment_data["values"][2]
        date = appointment_data["values"][3]

        cursor.execute("DELETE FROM appointments WHERE client_id=(SELECT id FROM clients WHERE forename || ' ' || surname = ?) AND staff_id=(SELECT id FROM staff WHERE forename || ' ' || surname = ?) AND session_time=? AND session_date=?", (client_name, staff_name, time, date))

        conn.commit()
        conn.close()

        self.load_appointments()

    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class AddAppointmentWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Appointment")
        self.geometry("400x400")
        self.create_widgets()

    def create_widgets(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        # Fetch staff and clients
        cursor.execute("SELECT id, forename, surname FROM staff")
        self.staff = [{"id": s[0], "name": f"{s[1]} {s[2]}"} for s in cursor.fetchall()]

        cursor.execute("SELECT id, forename, surname FROM clients")
        self.clients = [{"id": c[0], "name": f"{c[1]} {c[2]}"} for c in cursor.fetchall()]

        conn.close()

        # Staff dropdown
        self.staff_var = tk.StringVar()
        self.staff_dropdown = ttk.Combobox(self, textvariable=self.staff_var, values=[s["name"] for s in self.staff])
        self.staff_dropdown.grid(row=0, column=1)
        ttk.Label(self, text="Staff:").grid(row=0, column=0)

        # Client dropdown
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(self, textvariable=self.client_var, values=[c["name"] for c in self.clients])
        self.client_dropdown.grid(row=1, column=1)
        ttk.Label(self, text="Client:").grid(row=1, column=0)

        # Time input
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(self, textvariable=self.time_var)
        self.time_entry.grid(row=2, column=1)
        ttk.Label(self, text="Time (HH:MM):").grid(row=2, column=0)

        # Date input
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(self, textvariable=self.date_var)
        self.date_entry.grid(row=3, column=1)
        ttk.Label(self, text="Date (DD-MM-YY):").grid(row=3, column=0)

        # Status
        self.status_var = tk.StringVar(value="Pending")  # Default to "Pending"
        
        # Comments
        self.comments_var = tk.StringVar()
        self.comments_entry = ttk.Entry(self, textvariable=self.comments_var)
        self.comments_entry.grid(row=4, column=1)
        ttk.Label(self, text="Comments:").grid(row=4, column=0)

        # Submit Button
        ttk.Button(self, text="Submit", command=self.add_to_database).grid(row=5, column=0, columnspan=2)

    def add_to_database(self):
        selected_staff = [s for s in self.staff if s["name"] == self.staff_var.get()][0]
        selected_client = [c for c in self.clients if c["name"] == self.client_var.get()][0]
        time = self.time_var.get()
        date = self.date_var.get()

        # Basic validation
        if not self.staff_var.get() or not self.client_var.get() or not time or not date:
            messagebox.showerror("Error", "Please fill out all fields!")
            return
        
        # Format checks for time and date can be added here if needed
        
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO appointments (client_id, staff_id, session_time, session_date, status, comments) VALUES (?, ?, ?, ?, ?, ?)", 
                       (selected_client["id"], selected_staff["id"], time, date, self.status_var.get(), self.comments_var.get()))
        
        conn.commit()
        conn.close()

        self.parent.load_appointments()
        self.destroy()

class EditAppointmentWindow(tk.Toplevel):
    def __init__(self, parent, appointment_id):
        super().__init__(parent)
        self.parent = parent
        self.appointment_id = appointment_id
        self.title("Edit Appointment")
        self.geometry("400x400")
        self.create_widgets()
        self.load_appointment_data()

    def create_widgets(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        # Fetch staff and clients
        cursor.execute("SELECT id, forename, surname FROM staff")
        self.staff = [{"id": s[0], "name": f"{s[1]} {s[2]}"} for s in cursor.fetchall()]

        cursor.execute("SELECT id, forename, surname FROM clients")
        self.clients = [{"id": c[0], "name": f"{c[1]} {c[2]}"} for c in cursor.fetchall()]

        conn.close()

        # Staff dropdown
        self.staff_var = tk.StringVar()
        self.staff_dropdown = ttk.Combobox(self, textvariable=self.staff_var, values=[s["name"] for s in self.staff])
        self.staff_dropdown.grid(row=0, column=1)
        ttk.Label(self, text="Staff:").grid(row=0, column=0)

        # Client dropdown
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(self, textvariable=self.client_var, values=[c["name"] for c in self.clients])
        self.client_dropdown.grid(row=1, column=1)
        ttk.Label(self, text="Client:").grid(row=1, column=0)

        # Time input
        self.time_var = tk.StringVar()
        self.time_entry = ttk.Entry(self, textvariable=self.time_var)
        self.time_entry.grid(row=2, column=1)
        ttk.Label(self, text="Time (HH:MM):").grid(row=2, column=0)

        # Date input
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(self, textvariable=self.date_var)
        self.date_entry.grid(row=3, column=1)
        ttk.Label(self, text="Date (DD-MM-YY):").grid(row=3, column=0)

        # Status dropdown
        self.status_options = ["Pending", "Completed", "Cancelled"]
        self.status_var = tk.StringVar()
        self.status_dropdown = ttk.Combobox(self, textvariable=self.status_var, values=self.status_options, state="readonly")
        self.status_dropdown.grid(row=5, column=1)
        ttk.Label(self, text="Status:").grid(row=5, column=0)
        
        # Comments
        self.comments_var = tk.StringVar()
        self.comments_entry = ttk.Entry(self, textvariable=self.comments_var)
        self.comments_entry.grid(row=6, column=1)
        ttk.Label(self, text="Comments:").grid(row=6, column=0)

        # Submit Button
        ttk.Button(self, text="Update", command=self.update_to_database).grid(row=7, column=0, columnspan=2)

    def load_appointment_data(self):
        # Connect to the database
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        # Fetch the appointment's details based on the appointment ID
        cursor.execute("SELECT c.forename || ' ' || c.surname, s.forename || ' ' || s.surname, a.session_time, a.session_date, a.status, a.comments \
                        FROM appointments a \
                        INNER JOIN clients c ON a.client_id = c.id \
                        INNER JOIN staff s ON a.staff_id = s.id WHERE a.id = ?", (self.appointment_id,))
        data = cursor.fetchone()

        # Populate widgets with the data
        self.staff_dropdown.set(data[1])
        self.client_dropdown.set(data[0])
        self.time_entry.insert(0, data[2])
        self.date_entry.insert(0, data[3])
        self.comments_entry.insert(0, data[5])

        # Set the status dropdown to the current status
        self.status_var.set(data[4])   # Assuming the fifth element in the fetched data is the appointment's status

        conn.close()

    def update_to_database(self):
        # Collect all data from widgets
        staff_name = self.staff_var.get()
        client_name = self.client_var.get()
        time = self.time_var.get()
        date = self.date_var.get()
        status = self.status_var.get()
        comments = self.comments_entry.get()

        # Validate (to ensure no empty fields)
        if not all([staff_name, client_name, time, date]):
            messagebox.showerror("Error", "All fields except comments must be filled!")
            return

        # Database Update Operation
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        # Get staff and client IDs
        cursor.execute("SELECT id FROM staff WHERE forename || ' ' || surname = ?", (staff_name,))
        staff_id = cursor.fetchone()[0]

        cursor.execute("SELECT id FROM clients WHERE forename || ' ' || surname = ?", (client_name,))
        client_id = cursor.fetchone()[0]

        # Update the appointment
        cursor.execute("UPDATE appointments SET staff_id=?, client_id=?, session_time=?, session_date=?, status=?, comments=? WHERE id=?", 
                       (staff_id, client_id, time, date, status, comments, self.appointment_id))
        
        conn.commit()
        conn.close()

        self.parent.load_appointments()
        self.destroy()

class ClientsPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self, text="Clients Page")
        self.label.pack(pady=10)

        # Client listbox
        self.client_listbox = tk.Listbox(self)
        self.client_listbox.pack(pady=20)
        self.client_listbox.bind('<<ListboxSelect>>', self.client_selected)

        # Load clients into listbox
        self.load_clients()

        # View  selected client details
        self.view_client_button = ttk.Button(self, text="View Client", command=self.view_client)
        self.view_client_button.pack(pady=10)



        # Export selected client
        self.export_specific_client_button = ttk.Button(self, text="Export Selected Client", command=self.export_specific_client, state=tk.DISABLED)
        self.export_specific_client_button.pack(pady=10)
    
        # Adding the new buttons for Add, Edit, Remove
        self.add_client_button = ttk.Button(self, text="Add Client", command=self.add_client)
        self.add_client_button.pack(pady=10)

        self.edit_client_button = ttk.Button(self, text="Edit Client", command=self.edit_client)
        self.edit_client_button.pack(pady=10)

        self.remove_client_button = ttk.Button(self, text="Remove Client", command=self.remove_client)
        self.remove_client_button.pack(pady=10)

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.pack(pady=20)
    
    def add_client(self):
        new_client_window = AddClientWindow(self)

    def view_client(self):
        if not self.client_listbox.curselection():
            messagebox.showerror("Error", "Please select a client to view!")
            return

        client_id = self.client_listbox.curselection()[0] + 1
        ViewClientWindow(self, client_id)

    def edit_client(self):
        client_id = self.client_listbox.curselection()
        if not client_id:
            messagebox.showerror("Error", "Please select a client to edit!")
            return

        # Launch the Edit Client window
        EditClientWindow(self, client_id[0] + 1)  # +1 because listbox indices start from 0 and ids from 1


    def remove_client(self):
        if not self.client_listbox.curselection():
            messagebox.showerror("Error", "Please select a client to remove!")
            return

        response = messagebox.askyesno("Confirmation", "Are you sure you want to remove this client?")
        if response:
            client_id = self.client_listbox.curselection()[0] + 1
            conn = sqlite3.connect("physiotherapy.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
            conn.commit()
            conn.close()

            # Reload the listbox
            self.load_clients()

            # Check if listbox is empty and disable the "Export Selected Client" button if it is
            if not self.client_listbox.size():
                self.export_specific_client_button.config(state=tk.DISABLED)


    def load_clients(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, forename, surname FROM clients")
        clients = cursor.fetchall()
        conn.close()

        # Clear listbox
        self.client_listbox.delete(0, tk.END)

        # Populate listbox
        for client in clients:
            self.client_listbox.insert(tk.END, f"{client[1]} {client[2]}")

    def client_selected(self, event):
        self.export_specific_client_button.config(state=tk.NORMAL)

        # Fetching the selected client's ID based on listbox selection
        index = self.client_listbox.curselection()[0] if self.client_listbox.curselection() else None
        if index is not None:
            conn = sqlite3.connect("physiotherapy.db")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM clients ORDER BY id LIMIT 1 OFFSET ?", (index,))
            self.selected_client_id = cursor.fetchone()[0]
            conn.close()
        else:
            self.selected_client_id = None

    def export_specific_client(self):
        client_id = self.client_listbox.curselection()
        if not client_id:
            messagebox.showerror("Error", "Please select a client to export!")
            return

        # Fetching the specific client's data from the database
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id=?", (client_id[0] + 1,))  # +1 as listbox indices start from 0 and ids from 1
        client = cursor.fetchone()
        conn.close()

        # Exporting the selected client data to a CSV
        filename = f"client_{client[0]}_export.csv"
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Forename", "Surname", "DOB", "Gender", "Phone", "Email", "Comments"])  # Header
            writer.writerow(client)

        messagebox.showinfo("Success", f"Client data exported to {filename}")

    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class AddClientWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Client")
        self.geometry("300x400")

        self.create_widgets()

    def create_widgets(self):
        # Entry for Forename
        ttk.Label(self, text="*Forename:").grid(row=0, column=0, padx=10, pady=10)
        self.forename_entry = ttk.Entry(self)
        self.forename_entry.grid(row=0, column=1)

        # Entry for Surname
        ttk.Label(self, text="*Surname:").grid(row=1, column=0, padx=10, pady=10)
        self.surname_entry = ttk.Entry(self)
        self.surname_entry.grid(row=1, column=1)

        # Entry for DOB
        ttk.Label(self, text="DOB (DD-MM-YY):").grid(row=2, column=0, padx=10, pady=10)
        self.dob_entry = ttk.Entry(self)
        self.dob_entry.grid(row=2, column=1)

        # Combobox for Gender
        ttk.Label(self, text="Gender:").grid(row=3, column=0, padx=10, pady=10)
        self.gender_var = tk.StringVar()
        self.gender_combobox = ttk.Combobox(self, textvariable=self.gender_var, values=["Male", "Female", "Other"])
        self.gender_combobox.grid(row=3, column=1)

        # Entry for Phone
        ttk.Label(self, text="*Phone:").grid(row=4, column=0, padx=10, pady=10)
        self.phone_entry = ttk.Entry(self)
        self.phone_entry.grid(row=4, column=1)

        # Entry for Email
        ttk.Label(self, text="Email:").grid(row=5, column=0, padx=10, pady=10)
        self.email_entry = ttk.Entry(self)
        self.email_entry.grid(row=5, column=1)

        # Entry for Comments
        ttk.Label(self, text="Comments:").grid(row=6, column=0, padx=10, pady=10)
        self.comments_entry = ttk.Entry(self)
        self.comments_entry.grid(row=6, column=1)

        # Submit Button
        self.submit_button = ttk.Button(self, text="Add Client", command=self.add_to_database)
        self.submit_button.grid(row=7, column=0, columnspan=2, pady=20)

    def add_to_database(self):
        forename = self.forename_entry.get()
        surname = self.surname_entry.get()
        dob = self.dob_entry.get()
        gender = self.gender_combobox.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        comments = self.comments_entry.get()

        # Check if mandatory fields are filled out
        if not forename or not surname or not phone:
            messagebox.showerror("Error", "Please fill out all mandatory fields marked with *")
            return

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO clients (forename, surname, dob, gender, phone, email, comments) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                       (forename, surname, dob, gender, phone, email, comments))
        
        conn.commit()
        conn.close()

        # Update client listbox in parent (ClientsPage)
        self.parent.load_clients()
        self.destroy()

class EditClientWindow(tk.Toplevel):
    def __init__(self, parent, client_id):
        super().__init__(parent)
        self.parent = parent
        self.client_id = client_id
        self.title("Edit Client")
        self.geometry("300x400")
        
        # Variables for the form fields
        self.forename_var = tk.StringVar()
        self.surname_var = tk.StringVar()
        self.dob_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.comments_var = tk.StringVar()
        
        # Populate the variables with the existing client's data
        self.load_client_data()
        
        # Create the form
        ttk.Label(self, text="*Forename:").grid(row=0, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.forename_var).grid(row=0, column=1)
        
        ttk.Label(self, text="*Surname:").grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.surname_var).grid(row=1, column=1)
        
        ttk.Label(self, text="DOB (DD-MM-YY):").grid(row=2, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.dob_var).grid(row=2, column=1)
        
        ttk.Label(self, text="Gender:").grid(row=3, column=0, padx=10, pady=10)
        ttk.Combobox(self, textvariable=self.gender_var, values=["Male", "Female"]).grid(row=3, column=1)
        
        ttk.Label(self, text="*Phone:").grid(row=4, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.phone_var).grid(row=4, column=1)
        
        ttk.Label(self, text="Email:").grid(row=5, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.email_var).grid(row=5, column=1)
        
        ttk.Label(self, text="Comments:").grid(row=6, column=0, padx=10, pady=10)
        ttk.Entry(self, textvariable=self.comments_var).grid(row=6, column=1)
        
        # Update client button
        ttk.Button(self, text="Update Client", command=self.update_client).grid(row=8, columnspan=2, padx=10, pady=20)

    def load_client_data(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id=?", (self.client_id,))
        client = cursor.fetchone()
        conn.close()

        self.forename_var.set(client[1])
        self.surname_var.set(client[2])
        self.dob_var.set(client[3])
        self.gender_var.set(client[4])
        self.phone_var.set(client[5])
        self.email_var.set(client[6])
        self.comments_var.set(client[7])

    def update_client(self):
        forename = self.forename_var.get()
        surname = self.surname_var.get()
        phone = self.phone_var.get()
        
        if not forename or not surname or not phone:
            messagebox.showerror("Error", "Please fill out all mandatory fields marked with *")
            return

        dob = self.dob_var.get()
        gender = self.gender_var.get()
        email = self.email_var.get()
        comments = self.comments_var.get()
        
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clients 
            SET forename=?, surname=?, dob=?, gender=?, phone=?, email=?, comments=? 
            WHERE id=?""", 
            (forename, surname, dob, gender, phone, email, comments, self.client_id))
        conn.commit()
        conn.close()
        
        self.parent.load_clients()
        self.destroy()

class ViewClientWindow(tk.Toplevel):
    def __init__(self, parent, client_id):
        super().__init__(parent)
        self.client_id = client_id
        self.title("View Client")
        self.geometry("300x400")
        self.load_client_data()

    def load_client_data(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id=?", (self.client_id,))
        client = cursor.fetchone()
        conn.close()

    

        if client:
            ttk.Label(self, text="Client ID:").grid(row=0, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[0]).grid(row=0, column=1)

            ttk.Label(self, text="Forename:").grid(row=1, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[1]).grid(row=1, column=1)
            
            ttk.Label(self, text="Surname:").grid(row=2, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[2]).grid(row=2, column=1)
            
            ttk.Label(self, text="DOB:").grid(row=3, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[3]).grid(row=3, column=1)

            ttk.Label(self, text="Gender:").grid(row=4, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[4]).grid(row=4, column=1)

            ttk.Label(self, text="Phone:").grid(row=5, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[5]).grid(row=5, column=1)
            
            ttk.Label(self, text="Email:").grid(row=6, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[6]).grid(row=6, column=1)
            
            ttk.Label(self, text="Comments:").grid(row=7, column=0, padx=10, pady=10)
            ttk.Label(self, text=client[7]).grid(row=7, column=1)
        else:
            ttk.Label(self, text="No client data found.").grid(row=0, column=0, padx=10, pady=10)

class StaffPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self, text="Staff Page")
        self.label.pack(pady=10)

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.add_button = ttk.Button(self, text="Add Staff", command=self.open_add_staff_window)
        self.add_button.pack(pady=10)

        self.edit_button = ttk.Button(self, text="Edit Staff", command=self.open_edit_staff_window)
        self.edit_button.pack(pady=10)

        self.remove_button = ttk.Button(self, text="Remove Staff", command=self.remove_staff)
        self.remove_button.pack(pady=10)

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.pack(pady=20)
    
        self.load_staff()

    def load_staff(self):
        self.listbox.delete(0, tk.END)  # Clear current list
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, forename, surname, access_level FROM staff")
        staff_members = cursor.fetchall()
        for member in staff_members:
            self.listbox.insert(tk.END, f"ID: {member[0]}, Username: {member[1]}, Name: {member[2]} {member[3]}, Access Level: {member[4]}")
        conn.close()

    def open_add_staff_window(self):
        AddStaffWindow(self)

    def open_edit_staff_window(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a staff member to edit!")
            return
        selected_id = int(self.listbox.get(selected_index).split(",")[0].split(":")[1].strip())
        EditStaffWindow(self, selected_id)

    def remove_staff(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select a staff member to remove!")
            return

        # Extract the ID of the selected staff member
        selected_id = int(self.listbox.get(selected_index).split(",")[0].split(":")[1].strip())

        # Ask for confirmation
        response = messagebox.askyesno("Confirmation", "Are you sure you want to remove this staff member?")
        if response:
            # Remove the staff member from the database
            conn = sqlite3.connect("physiotherapy.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM staff WHERE id=?", (selected_id,))
            conn.commit()
            conn.close()

            # Refresh the listbox
            self.load_staff()
        
    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class AddStaffWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Staff")
        self.geometry("400x300")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        ttk.Label(self, text="Forename:").grid(row=2, column=0, padx=10, pady=10)
        self.forename_entry = ttk.Entry(self)
        self.forename_entry.grid(row=2, column=1)

        ttk.Label(self, text="Surname:").grid(row=3, column=0, padx=10, pady=10)
        self.surname_entry = ttk.Entry(self)
        self.surname_entry.grid(row=3, column=1)

        ttk.Label(self, text="Access Level:").grid(row=4, column=0, padx=10, pady=10)
        self.access_var = tk.StringVar()
        self.access_dropdown = ttk.Combobox(self, textvariable=self.access_var, values=["1", "2", "3"])
        self.access_dropdown.grid(row=4, column=1)

        ttk.Button(self, text="Submit", command=self.add_to_database).grid(row=5, column=0, columnspan=2, pady=20)

    def add_to_database(self):
        username = self.username_entry.get()
        password = self.password_entry.get()  # You may want to hash this
        forename = self.forename_entry.get()
        surname = self.surname_entry.get()
        access_level = self.access_var.get()

        if not username or not password or not forename or not surname:
            messagebox.showerror("Error", "Please fill out all fields!")
            return

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO staff (username, password, forename, surname, access_level) VALUES (?, ?, ?, ?, ?)", 
                       (username, password, forename, surname, access_level))
        
        conn.commit()
        conn.close()

        self.parent.load_staff()
        self.destroy()

class EditStaffWindow(tk.Toplevel):
    def __init__(self, parent, staff_id):
        super().__init__(parent)
        self.parent = parent
        self.staff_id = staff_id
        self.title("Edit Staff")
        self.geometry("400x300")
        self.create_widgets()
        self.load_staff_data()

    def create_widgets(self):
        ttk.Label(self, text="Username:").grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = ttk.Entry(self)
        self.username_entry.grid(row=0, column=1)

        ttk.Label(self, text="Password:").grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1)

        ttk.Label(self, text="Forename:").grid(row=2, column=0, padx=10, pady=10)
        self.forename_entry = ttk.Entry(self)
        self.forename_entry.grid(row=2, column=1)

        ttk.Label(self, text="Surname:").grid(row=3, column=0, padx=10, pady=10)
        self.surname_entry = ttk.Entry(self)
        self.surname_entry.grid(row=3, column=1)

        ttk.Label(self, text="Access Level:").grid(row=4, column=0, padx=10, pady=10)
        self.access_var = tk.StringVar(self)
        self.access_dropdown = ttk.Combobox(self, textvariable=self.access_var, values=["1", "2", "3"])
        self.access_dropdown.grid(row=4, column=1)

        ttk.Button(self, text="Save Changes", command=self.update_database).grid(row=5, column=0, columnspan=2, pady=20)

    def load_staff_data(self):
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, forename, surname, access_level FROM staff WHERE id = ?", (self.staff_id,))
        data = cursor.fetchone()
        conn.close()

        if data:
            self.username_entry.insert(0, data[0])
            self.password_entry.insert(0, data[1])  # NOTE: Displaying passwords can be a security risk
            self.forename_entry.insert(0, data[2])
            self.surname_entry.insert(0, data[3])
            self.access_var.set(data[4])

    def update_database(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        forename = self.forename_entry.get()
        surname = self.surname_entry.get()
        access_level = self.access_var.get()

        if not username or not password or not forename or not surname:
            messagebox.showerror("Error", "Please fill out all fields!")
            return

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE staff SET username=?, password=?, forename=?, surname=?, access_level=? WHERE id=?", 
                       (username, password, forename, surname, access_level, self.staff_id))
        
        conn.commit()
        conn.close()

        self.parent.load_staff()
        self.destroy()

class InventoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()


    def create_widgets(self):


        # Create the Treeview to show the table
        self.tree = ttk.Treeview(self, columns=("item_id", "item_name", "quantity", "expiry_date", "supplier", "cost_price"), show='headings')

        # Adjusting the column width
        self.tree.column("item_id", width=70)
        self.tree.column("item_name", width=200)
        self.tree.column("quantity", width=70)
        self.tree.column("expiry_date", width=120)
        self.tree.column("supplier", width=100)
        self.tree.column("cost_price", width=80)

        self.tree.heading("item_id", text="Item ID")
        self.tree.heading("item_name", text="Item Name")
        self.tree.heading("quantity", text="Quantity")
        self.tree.heading("expiry_date", text="Expiry Date")
        self.tree.heading("supplier", text="Supplier")
        self.tree.heading("cost_price", text="Cost Price")
        self.tree.pack(pady=20)

        # Buttons for Add, Edit and Delete
        self.add_button = ttk.Button(self, text="Add Item", command=self.add_item)
        self.add_button.pack(pady=10)

        self.edit_button = ttk.Button(self, text="Edit Item", command=self.edit_item)
        self.edit_button.pack(pady=10)

        self.delete_button = ttk.Button(self, text="Delete Item", command=self.delete_item)
        self.delete_button.pack(pady=10)

        # Add Return to Main Page button
        self.return_main_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_main_button.pack(pady=20)

        # Load items into the treeview
        self.load_items()

    def load_items(self):
        # Clear existing items in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Connect to the database
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        
        # Execute the SELECT query
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()

        # Insert each row into the Treeview
        for item in items:
            self.tree.insert("", "end", values=item)

        # Close the database connection
        conn.close()


    def add_item(self):
        AddItemWindow(self)

    def edit_item(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select an item to edit!")
            return
            
        item_details = self.tree.item(selected_item, "values")
        EditItemWindow(self, item_details)

    def delete_item(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showerror("Error", "Please select an item to delete!")
            return

        # Confirm deletion box
        response = messagebox.askyesno("Confirmation", "Are you sure you want to delete this item?")
        if response:
            # Get the item's ID from the treeview
            item_id_to_delete = self.tree.item(selected_item, "values")[0]

            # Connect to the database
            conn = sqlite3.connect("physiotherapy.db")
            cursor = conn.cursor()

            # Execute SQL command to delete the item with this item_id
            cursor.execute("DELETE FROM inventory WHERE id=?", (item_id_to_delete,))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

            # Refresh the treeview to reflect the deleted item
            self.load_items()


    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class AddItemWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Add Item")
        
        # Create Entry widgets and labels
        ttk.Label(self, text="Item Name:").grid(row=0, column=0)
        self.item_name_entry = ttk.Entry(self)
        self.item_name_entry.grid(row=0, column=1)

        ttk.Label(self, text="Quantity:").grid(row=1, column=0)
        self.quantity_entry = ttk.Entry(self)
        self.quantity_entry.grid(row=1, column=1)

        ttk.Label(self, text="Expiry Date:").grid(row=2, column=0)
        self.expiry_date_entry = ttk.Entry(self)
        self.expiry_date_entry.grid(row=2, column=1)

        ttk.Label(self, text="Supplier:").grid(row=3, column=0)
        self.supplier_entry = ttk.Entry(self)
        self.supplier_entry.grid(row=3, column=1)

        ttk.Label(self, text="Cost Price:").grid(row=4, column=0)
        self.cost_price_entry = ttk.Entry(self)
        self.cost_price_entry.grid(row=4, column=1)

        ttk.Button(self, text="Submit", command=self.submit_to_database).grid(row=5, column=0, columnspan=2)

    def submit_to_database(self):
        item_name = self.item_name_entry.get()
        quantity = self.quantity_entry.get()
        expiry_date = self.expiry_date_entry.get()
        supplier = self.supplier_entry.get()
        cost_price = self.cost_price_entry.get()

        if not item_name or not quantity:
            messagebox.showerror("Error", "Please fill out the mandatory fields!")
            return

        # Insert the data into the database
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO inventory (item_name, quantity, expiry_date, supplier, cost_price)
            VALUES (?, ?, ?, ?, ?)
        """, (item_name, quantity, expiry_date, supplier, cost_price))

        conn.commit()
        conn.close()

        # Refresh the main table to reflect the new item and close the window
        self.parent.load_items()
        self.destroy()

class EditItemWindow(tk.Toplevel):
    def __init__(self, parent, item_details):
        super().__init__(parent)
        self.parent = parent
        self.item_details = item_details
        self.title("Edit Item")
        self.geometry("500x300")  
        
        self.create_widgets()

    def create_widgets(self):
        self.label_name = tk.Label(self, text="Item Name:")
        self.label_name.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_name = tk.Entry(self)
        self.entry_name.grid(row=0, column=1, padx=10, pady=10)
        self.entry_name.insert(0, self.item_details[1])  # pre-fill with existing item name

        self.label_quantity = tk.Label(self, text="Quantity:")
        self.label_quantity.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_quantity = tk.Entry(self)
        self.entry_quantity.grid(row=1, column=1, padx=10, pady=10)
        self.entry_quantity.insert(0, self.item_details[2])  # pre-fill with existing quantity

        self.label_expiry = tk.Label(self, text="Expiry Date:")
        self.label_expiry.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_expiry = tk.Entry(self)
        self.entry_expiry.grid(row=2, column=1, padx=10, pady=10)
        self.entry_expiry.insert(0, self.item_details[3])  # pre-fill with existing expiry date

        self.label_supplier = tk.Label(self, text="Supplier:")
        self.label_supplier.grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_supplier = tk.Entry(self)
        self.entry_supplier.grid(row=3, column=1, padx=10, pady=10)
        self.entry_supplier.insert(0, self.item_details[4])  # pre-fill with existing supplier

        self.label_price = tk.Label(self, text="Cost Price:")
        self.label_price.grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)

        self.entry_price = tk.Entry(self)
        self.entry_price.grid(row=4, column=1, padx=10, pady=10)
        self.entry_price.insert(0, self.item_details[5])  # pre-fill with existing cost price

        self.btn_submit = tk.Button(self, text="Update Item", command=self.update_item)
        self.btn_submit.grid(row=5, column=0, columnspan=2, pady=20)

    def update_item(self):
        item_id = self.item_details[0]
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        expiry = self.entry_expiry.get()
        supplier = self.entry_supplier.get()
        price = self.entry_price.get()

        if not name or not quantity:
            messagebox.showerror("Error", "Item Name and Quantity are mandatory!")
            return

        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET item_name=?, quantity=?, expiry_date=?, supplier=?, cost_price=? WHERE id=?", (name, quantity, expiry, supplier, price, item_id))
        conn.commit()
        conn.close()

        self.parent.load_items()  # Refresh the treeview
        self.destroy()  # Close the Edit window


class PhysiotherapyApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # User access level
        self.access_level = None

        # Title and size
        self.title("Physiotherapy Management")
        self.geometry("800x600")

        # Menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        # Data management menu
        self.data_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="Data", menu=self.data_menu)
        self.data_menu.add_command(label="Backup Database", command=self.backup_database)
        self.data_menu.add_command(label="Restore Database", command=self.restore_database)
        self.data_menu.add_command(label="Export All Clients", command=self.export_all_clients)

        # Display the login window and hide the main window until login
        self.withdraw()
        login = LoginWindow(self)

    def setup_interface(self):
        # Destroy any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Set up the main interface
        self.main_page = MainPage(self)
        self.main_page.pack(fill=tk.BOTH, expand=True)

    def backup_database(self):
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        backup_file = os.path.join(downloads_path, "physiotherapy_backup.db")
        backup_file = "physiotherapy_backup.db"
        try:
            shutil.copy2('physiotherapy.db', backup_file)
            messagebox.showinfo("Success", f"Database backed up to {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def restore_database(self):
        backup_file = "physiotherapy_backup.db"
        try:
            shutil.copy2(backup_file, 'physiotherapy.db')
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed: {str(e)}")
        messagebox.showinfo("Success", f"Database restored from {backup_file}")


    def export_all_clients(self):
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        file_path = os.path.join(downloads_path, 'clients_export.csv')
        conn = sqlite3.connect("physiotherapy.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()

        with open('clients_export.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Forename", "Surname", "DOB", "Gender", "Phone", "Email", "Comments"])  # Header
            writer.writerows(clients)

        conn.close()
        messagebox.showinfo("Success", f"All clients exported to {file_path}")


    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search("[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search("[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search("[0-9]", password):
            return False, "Password must contain at least one digit."
        if not re.search("[!@#$%^&*]", password):
            return False, "Password must contain at least one special character (!@#$%^&*)."
        return True, "Valid password."

    def open_data_options(self):
        DataOptionsWindow(self)

if __name__ == "__main__":
    app = PhysiotherapyApp()
    app.mainloop()


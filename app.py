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
        self.grid(row=0, column=0, sticky="nsew")
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self.create_widgets()

    def create_widgets(self):
        # Here you can add the components for the Appointments page
        # such as filtering tools, lists of appointments, etc.
        # I'll keep it simple for brevity, but you can expand upon it.

        # Filter Section
        ttk.Label(self, text="Filter Appointments").grid(row=0, column=0, sticky='w', pady=10, padx=10)

        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(self, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=0, sticky='w', pady=10, padx=10)

        self.gender_var = tk.StringVar()
        self.gender_dropdown = ttk.Combobox(self, textvariable=self.gender_var, values=["Male", "Female"])
        self.gender_dropdown.grid(row=1, column=1, sticky='w', pady=10, padx=10)

        # ... You can add more filters like DOB, staff member, etc.

        self.filter_button = ttk.Button(self, text="Apply Filter", command=self.apply_filter)
        self.filter_button.grid(row=1, column=3, sticky='w', pady=10, padx=10)

        # Appointments List
        self.appointments_listbox = tk.Listbox(self, height=10, width=50)
        self.appointments_listbox.grid(row=2, column=0, columnspan=4, pady=10, padx=10)

        self.load_appointments()

        # Create New Appointment Button
        self.new_appointment_button = ttk.Button(self, text="Create New Appointment", command=self.new_appointment)
        self.new_appointment_button.grid(row=3, column=0, columnspan=4, pady=10)

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.grid(row=100, column=0, columnspan=4, pady=20)

    def load_appointments(self):
        # Sample code to load appointments. This should be replaced with actual database fetch calls.
        sample_data = ["Appointment 1", "Appointment 2", "Appointment 3"]
        for item in sample_data:
            self.appointments_listbox.insert(tk.END, item)

    def apply_filter(self):
        # Logic to apply filter and reload the appointments list
        pass

    def new_appointment(self):
        new_app_page = NewAppointmentPage(self)
        new_app_page.grid(row=6, column=0, columnspan=4, pady=10, padx=10, sticky='nsew')

    def return_to_main(self):
        self.clear_frame()
        self.destroy()
        self.parent.create_widgets()

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class NewAppointmentPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.create_widgets()

    def create_widgets(self):
        # Client dropdown, fetched from database
        self.client_var = tk.StringVar()
        self.client_dropdown = ttk.Combobox(self, textvariable=self.client_var, values=self.fetch_clients())
        self.client_dropdown.grid(row=0, column=1, sticky='w', pady=10, padx=10)

        # ... similar widgets for staff, session time/date, and status

        self.comment_var = tk.StringVar()
        self.comment_entry = ttk.Entry(self, textvariable=self.comment_var)
        self.comment_entry.grid(row=4, column=1, sticky='w', pady=10, padx=10)

        self.save_button = ttk.Button(self, text="Save Appointment", command=self.save_appointment)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=10)

    def fetch_clients(self):
        # Sample code. Replace with fetching client names from the database.
        return ["Client 1", "Client 2", "Client 3"]

    def save_appointment(self):
        # Logic to save the appointment to the database.
        pass

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

        # To be expanded upon with detailed staff management widgets.

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.pack(pady=20)

    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

class InventoryPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self, text="Inventory Page")
        self.label.pack(pady=10)

        # To be expanded upon with detailed inventory management widgets.

        # Button to return to main page
        self.return_button = ttk.Button(self, text="Return to Main Page", command=self.return_to_main)
        self.return_button.pack(pady=20)

    def return_to_main(self):
        self.clear_frame()
        self.destroy()  # Destroy the current sub-page frame
        self.parent.create_widgets()  # Then recreate the main page's widgets

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

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


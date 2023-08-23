# app.py
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import sqlite3

class Database:
    def __init__(self, db_name="database.db"):  # Default to database.db
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def query(self, sql, parameters=()):
        self.cursor.execute(sql, parameters)
        self.conn.commit()

    def fetch(self, sql, parameters=()):
        self.cursor.execute(sql, parameters)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


class BaseWindow:
    def __init__(self, master):
        self.master = master

    def open_new_window(self, window_class):
        new_window = tk.Toplevel(self.master)
        window_class(new_window)


class AppointmentsWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Manage Appointments")

        # Widgets for viewing appointments
        self.appointments_listbox = tk.Listbox(self.master)
        self.appointments_listbox.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        self.load_appointments()

        # Widgets for managing appointments
        self.add_appointment_label = tk.Label(self.master, text="Manage Appointment:")
        self.add_appointment_label.pack(pady=10)

        # Client's Name
        self.client_name_label = tk.Label(self.master, text="Client Name:")
        self.client_name_label.pack(anchor=tk.W, padx=20)
        self.client_name_entry = tk.Entry(self.master)
        self.client_name_entry.pack(fill=tk.X, padx=20, pady=5)

        # Client ID
        self.client_id_label = tk.Label(self.master, text="Client ID:")
        self.client_id_label.pack(anchor=tk.W, padx=20)
        self.client_id_entry = tk.Entry(self.master)
        self.client_id_entry.pack(fill=tk.X, padx=20, pady=5)

        # Session Date (Day picker)
        self.session_date_label = tk.Label(self.master, text="Session Date:")
        self.session_date_label.pack(anchor=tk.W, padx=20)
        self.session_date_button = tk.Button(self.master, text="Pick Date", command=self.pick_date)
        self.session_date_button.pack(pady=5)

        # Session Time (in HH:MM format)
        self.session_time_label = tk.Label(self.master, text="Session Time (HH:MM):")
        self.session_time_label.pack(anchor=tk.W, padx=20)
        self.session_time_entry = tk.Entry(self.master)
        self.session_time_entry.pack(fill=tk.X, padx=20, pady=5)

        # Session status
        self.session_status_label = tk.Label(self.master, text="Session Status:")
        self.session_status_label.pack(anchor=tk.W, padx=20)
        self.session_status_combobox = ttk.Combobox(self.master, values=["Pending", "Completed", "Cancelled"])
        self.session_status_combobox.pack(fill=tk.X, padx=20, pady=5)
        self.session_status_combobox.set("Pending")  # Default value

        # Session Comments
        self.session_comments_label = tk.Label(self.master, text="Session Comments:")
        self.session_comments_label.pack(anchor=tk.W, padx=20)
        self.session_comments_entry = tk.Entry(self.master)
        self.session_comments_entry.pack(fill=tk.X, padx=20, pady=5)

        self.add_appointment_button = tk.Button(self.master, text="Save Appointment", command=self.save_appointment)
        self.add_appointment_button.pack(pady=10)

        self.edit_appointment_button = tk.Button(self.master, text="Edit Selected Appointment", command=self.populate_appointment_details)
        self.edit_appointment_button.pack(pady=10)

        self.delete_appointment_button = tk.Button(self.master, text="Delete Selected Appointment", command=self.delete_appointment)
        self.delete_appointment_button.pack(pady=10)

    def load_appointments(self):
        """Load and display appointments from the database."""
        # Clear the current list
        self.appointments_listbox.delete(0, tk.END)
        
        db = Database()
        rows = db.query("SELECT * FROM session")
        
        if rows is None:
            db.close()
            return
        
        for appointment in rows:
            session_id = appointment["sessionID"]
            client_name = appointment["client_name"]
            date_time = appointment["session_datetime"]
            status = appointment["session_status"]

            # Add each appointment to the listbox
            self.appointments_listbox.insert(tk.END, f"{session_id}: {client_name} on {date_time} - {status}")
        
        db.close()

    def pick_date(self):
        """Opens a simple dialog for date picking."""
        self.session_date = simpledialog.askstring("Input", "Enter date in YYYY-MM-DD format:")


        """Save (add or update) an appointment in the database."""
        client_name = self.client_name_entry.get()
        client_id = self.client_id_entry.get()
        session_date = getattr(self, "session_date", None)
        session_time = self.session_time_entry.get()
        session_status = self.session_status_combobox.get()
        session_comments = self.session_comments_entry.get()

        db = Database()
    
        selected_indices = self.appointments_listbox.curselection()
        
        # Check if we're updating an existing appointment
        if selected_indices:
            selected = self.appointments_listbox.get(selected_indices[0])
            sessionID = int(selected.split(":")[0])
            db.query("UPDATE session SET client_name=?, client_id=?, session_datetime=?, session_status=?, comments=? WHERE sessionID=?", 
                    (client_name, client_id, f"{session_date} {session_time}", session_status, session_comments, sessionID))
        else: 
            db.query("INSERT INTO session (clientID, staffID, session_datetime, session_status, comments) VALUES (?, ?, ?, ?, ?)",
                    (client_id, staff_id, f"{session_date} {session_time}", session_status, session_comments))

        
        db.close()
        self.load_appointments()

        """Save (add or update) an appointment in the database."""
        client_name = self.client_name_entry.get()
        client_id = self.client_id_entry.get()
        session_date = getattr(self, "session_date", None)
        session_time = self.session_time_entry.get()
        session_status = self.session_status_combobox.get()
        session_comments = self.session_comments_entry.get()

        db = Database()
       
        # Check if we're updating an existing appointment
        selected = self.appointments_listbox.get(self.appointments_listbox.curselection())
        if selected:
            sessionID = int(selected.split(":")[0])
            db.query("UPDATE session SET client_name=?, client_id=?, session_datetime=?, session_status=?, comments=? WHERE sessionID=?", 
                     (client_name, client_id, f"{session_date} {session_time}", session_status, session_comments, sessionID))
        else: 
            db.query("INSERT INTO session (client_name, client_id, session_datetime, session_status, comments) VALUES (?, ?, ?, ?, ?)", 
                     (client_name, client_id, f"{session_date} {session_time}", session_status, session_comments))
        
        db.close()
        self.load_appointments()

    def save_appointment(self):
        """Save (add or update) an appointment in the database."""
        client_id = self.client_id_entry.get()
        session_date = getattr(self, "session_date", None)
        session_time = self.session_time_entry.get()
        session_status = self.session_status_combobox.get()
        session_comments = self.session_comments_entry.get()

        db = Database()

        selected_indices = self.appointments_listbox.curselection()
        
        # Check if we're updating an existing appointment
        if selected_indices:
            selected = self.appointments_listbox.get(selected_indices[0])
            sessionID = int(selected.split(":")[0])
            db.query("UPDATE session SET client_id=?, session_datetime=?, session_status=?, comments=? WHERE sessionID=?", 
                    (client_id, f"{session_date} {session_time}", session_status, session_comments, sessionID))
        else: 
            # I'm assuming a staffID must also be linked, you'll need to provide this
            staffID = ...  # Fetch the staffID, possibly from a dropdown or other input method.
            db.query("INSERT INTO session (client_id, staffID, session_datetime, session_status, comments) VALUES (?, ?, ?, ?, ?)", 
                    (client_id, staffID, f"{session_date} {session_time}", session_status, session_comments))

        db.close()
        self.load_appointments()

    def populate_appointment_details(self):
        """Populate input fields with details of the selected appointment."""
        selected = self.appointments_listbox.get(self.appointments_listbox.curselection())
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an appointment to edit.")
            return

        sessionID = int(selected.split(":")[0])
       
        db = Database()
        rows = db.query("SELECT * FROM session WHERE sessionID=?", (sessionID,))
        appointment = rows.fetchone()  # assuming sessionID is primary key and unique
        db.close()

        if appointment:
            datetime_str = appointment["session_datetime"]
            date_str, time_str = datetime_str.split(" ")
           
            self.client_name_entry.delete(0, tk.END)
            self.client_name_entry.insert(0, appointment["client_name"])
           
            self.client_id_entry.delete(0, tk.END)
            self.client_id_entry.insert(0, appointment["client_id"])
           
            self.session_date = date_str  # Store date separately to use later

            self.session_time_entry.delete(0, tk.END)
            self.session_time_entry.insert(0, time_str)
           
            self.session_status_combobox.set(appointment["session_status"])
           
            self.session_comments_entry.delete(0, tk.END)
            self.session_comments_entry.insert(0, appointment["comments"])

    def delete_appointment(self):
        """Delete a selected appointment."""
        if not self.appointments_listbox.get(0, tk.END):  # Check if listbox is empty
            messagebox.showinfo("Info", "No appointments found in the database to delete.")
            return

        selected = self.appointments_listbox.get(self.appointments_listbox.curselection())
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an appointment to delete.")
            return

        sessionID = int(selected.split(":")[0])

        db = Database()
        db.query("DELETE FROM session WHERE sessionID=?", (sessionID,))
        db.close()

        self.load_appointments()



class ClientDetailsWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Manage Client Details")
        
        # Widgets for viewing clients
        self.label = tk.Label(self.master, text="Clients List")
        self.label.pack(pady=10)

        self.clients_listbox = tk.Listbox(self.master, width=50, height=10)
        self.clients_listbox.pack(pady=20, padx=20)
        self.load_clients()

        # Widgets for adding a new client
        self.fields = ['Forename', 'Surname', 'DOB', 'Gender', 'Phone', 'Email', 'Comments']
        self.entries = {}

        for field in self.fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5, padx=20, fill=tk.X)

            label = tk.Label(frame, text=field, width=10)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field] = entry

        self.add_client_button = tk.Button(self.master, text="Add Client", command=self.add_client)
        self.add_client_button.pack(pady=10)

        self.edit_client_button = tk.Button(self.master, text="Edit Selected Client", command=self.edit_client)
        self.edit_client_button.pack(pady=10)

        self.delete_client_button = tk.Button(self.master, text="Delete Selected Client", command=self.delete_client)
        self.delete_client_button.pack(pady=10)

    def load_clients(self):
        """Load clients from the database into the listbox."""
        db = Database()
        clients = db.fetch("SELECT clientID, client_forename, client_surname FROM clientDetails")
        db.close()

        self.clients_listbox.delete(0, tk.END)
        for client in clients:
            self.clients_listbox.insert(tk.END, f"{client[0]}: {client[1]} {client[2]}")

    def add_client(self):
        """Add a new client to the database."""
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())
        
        db = Database()
        db.query("INSERT INTO clientDetails (client_forename, client_surname, DOB, gender, phone, email, comments) VALUES (?, ?, ?, ?, ?, ?, ?)", tuple(data))
        db.close()

        self.load_clients()

    def edit_client(self):
        """Edit the details of a selected client."""
        selected = self.clients_listbox.get(self.clients_listbox.curselection())
        if not selected:
            return

        clientID = int(selected.split(":")[0])
        
        # A dialog can be created to edit the client. For simplicity, I'm just using the existing entries.
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("UPDATE clientDetails SET client_forename=?, client_surname=?, DOB=?, gender=?, phone=?, email=?, comments=? WHERE clientID=?", tuple(data + [clientID]))
        db.close()

        self.load_clients()

    def delete_client(self):
        """Delete a selected client."""
        selected = self.clients_listbox.get(self.clients_listbox.curselection())
        if not selected:
            return

        clientID = int(selected.split(":")[0])

        db = Database()
        db.query("DELETE FROM clientDetails WHERE clientID=?", (clientID,))
        db.close()

        self.load_clients()


class StaffPermissionsWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Manage Staff Permissions")

        # Widgets for viewing staff members
        self.label = tk.Label(self.master, text="Staff List with Permissions")
        self.label.pack(pady=10)

        self.staff_listbox = tk.Listbox(self.master, width=50, height=10)
        self.staff_listbox.pack(pady=20, padx=20)
        self.load_staff()

        # Widgets for managing staff permissions
        self.fields = ['Username', 'Forename', 'Surname', 'Access Level']
        self.entries = {}

        for field in self.fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5, padx=20, fill=tk.X)

            label = tk.Label(frame, text=field, width=15)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field] = entry

        self.add_staff_button = tk.Button(self.master, text="Add Staff", command=self.add_staff)
        self.add_staff_button.pack(pady=10)

        self.edit_permission_button = tk.Button(self.master, text="Edit Selected Staff Permission", command=self.edit_permission)
        self.edit_permission_button.pack(pady=10)

        self.delete_staff_button = tk.Button(self.master, text="Delete Selected Staff", command=self.delete_staff)
        self.delete_staff_button.pack(pady=10)

    def load_staff(self):
        """Load staff members and their permissions from the database into the listbox."""
        db = Database()
        staff_members = db.fetch("SELECT staffID, username, staff_forename, staff_surname, access_level FROM staffDetails")
        db.close()

        self.staff_listbox.delete(0, tk.END)
        for staff in staff_members:
            self.staff_listbox.insert(tk.END, f"{staff[0]}: {staff[1]} - {staff[2]} {staff[3]} (Access Level: {staff[4]})")

    def add_staff(self):
        """Add a new staff member to the database."""
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("INSERT INTO staffDetails (username, staff_forename, staff_surname, access_level) VALUES (?, ?, ?, ?)", tuple(data))
        db.close()

        self.load_staff()

    def edit_permission(self):
        """Edit the permissions of a selected staff member."""
        selected = self.staff_listbox.get(self.staff_listbox.curselection())
        if not selected:
            return

        staffID = int(selected.split(":")[0])
        access_level = self.entries['Access Level'].get()

        db = Database()
        db.query("UPDATE staffDetails SET access_level=? WHERE staffID=?", (access_level, staffID))
        db.close()

        self.load_staff()

    def delete_staff(self):
        """Delete a selected staff member."""
        selected = self.staff_listbox.get(self.staff_listbox.curselection())
        if not selected:
            return

        staffID = int(selected.split(":")[0])

        db = Database()
        db.query("DELETE FROM staffDetails WHERE staffID=?", (staffID,))
        db.close()

        self.load_staff()


class InventoryWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Manage Inventory")

        # Widgets for viewing inventory items
        self.label = tk.Label(self.master, text="Inventory List")
        self.label.pack(pady=10)

        self.inventory_listbox = tk.Listbox(self.master, width=70, height=10)
        self.inventory_listbox.pack(pady=20, padx=20)
        self.load_inventory()

        # Widgets for adding and editing items in inventory
        self.fields = ['Item Name', 'Quantity', 'Expiry Date', 'Supplier', 'Cost Price']
        self.entries = {}

        for field in self.fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5, padx=20, fill=tk.X)

            label = tk.Label(frame, text=field, width=15)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field] = entry

        self.add_item_button = tk.Button(self.master, text="Add Item", command=self.add_item)
        self.add_item_button.pack(pady=10)

        self.edit_item_button = tk.Button(self.master, text="Edit Selected Item", command=self.edit_item)
        self.edit_item_button.pack(pady=10)

        self.delete_item_button = tk.Button(self.master, text="Delete Selected Item", command=self.delete_item)
        self.delete_item_button.pack(pady=10)

    def load_inventory(self):
        """Load items from the database into the listbox."""
        db = Database()
        items = db.fetch("SELECT itemID, itemName, quantity, expiraryDate, supplier, cost_price FROM inventory")
        db.close()

        self.inventory_listbox.delete(0, tk.END)
        for item in items:
            self.inventory_listbox.insert(tk.END, f"{item[0]}: {item[1]} (Qty: {item[2]}) - Expires: {item[3]} - Supplier: {item[4]} - Cost: ${item[5]}")

    def add_item(self):
        """Add a new item to the inventory."""
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("INSERT INTO inventory (itemName, quantity, expiraryDate, supplier, cost_price) VALUES (?, ?, ?, ?, ?)", tuple(data))
        db.close()

        self.load_inventory()

    def edit_item(self):
        """Edit the details of a selected inventory item."""
        selected = self.inventory_listbox.get(self.inventory_listbox.curselection())
        if not selected:
            return

        itemID = int(selected.split(":")[0])
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("UPDATE inventory SET itemName=?, quantity=?, expiraryDate=?, supplier=?, cost_price=? WHERE itemID=?", tuple(data + [itemID]))
        db.close()

        self.load_inventory()

    def delete_item(self):
        """Delete a selected item from the inventory."""
        selected = self.inventory_listbox.get(self.inventory_listbox.curselection())
        if not selected:
            return

        itemID = int(selected.split(":")[0])

        db = Database()
        db.query("DELETE FROM inventory WHERE itemID=?", (itemID,))
        db.close()

        self.load_inventory()


class TransactionsWindow(BaseWindow):
    def __init__(self, master):
        super().__init__(master)
        self.master.title("Manage Transactions")

        # Widgets for viewing transactions
        self.label = tk.Label(self.master, text="Transactions List")
        self.label.pack(pady=10)

        self.transactions_listbox = tk.Listbox(self.master, width=70, height=10)
        self.transactions_listbox.pack(pady=20, padx=20)
        self.load_transactions()

        # Widgets for adding and editing transactions
        self.fields = ['Transaction Date', 'Transaction Type', 'Amount', 'Description']
        self.entries = {}

        for field in self.fields:
            frame = tk.Frame(self.master)
            frame.pack(pady=5, padx=20, fill=tk.X)

            label = tk.Label(frame, text=field, width=20)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.entries[field] = entry

        self.add_transaction_button = tk.Button(self.master, text="Add Transaction", command=self.add_transaction)
        self.add_transaction_button.pack(pady=10)

        self.edit_transaction_button = tk.Button(self.master, text="Edit Selected Transaction", command=self.edit_transaction)
        self.edit_transaction_button.pack(pady=10)

        self.delete_transaction_button = tk.Button(self.master, text="Delete Selected Transaction", command=self.delete_transaction)
        self.delete_transaction_button.pack(pady=10)

    def load_transactions(self):
        """Load transactions from the database into the listbox."""
        db = Database()
        # Assuming a 'transactions' table exists in the database for this example
        transactions = db.fetch("SELECT transactionID, transaction_date, transaction_type, amount, description FROM transactions")
        db.close()

        self.transactions_listbox.delete(0, tk.END)
        for transaction in transactions:
            self.transactions_listbox.insert(tk.END, f"{transaction[0]}: {transaction[1]} - {transaction[2]} - Amount: ${transaction[3]} - {transaction[4]}")

    def add_transaction(self):
        """Add a new transaction to the database."""
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("INSERT INTO transactions (transaction_date, transaction_type, amount, description) VALUES (?, ?, ?, ?)", tuple(data))
        db.close()

        self.load_transactions()

    def edit_transaction(self):
        """Edit the details of a selected transaction."""
        selected = self.transactions_listbox.get(self.transactions_listbox.curselection())
        if not selected:
            return

        transactionID = int(selected.split(":")[0])
        data = []
        for field in self.fields:
            data.append(self.entries[field].get())

        db = Database()
        db.query("UPDATE transactions SET transaction_date=?, transaction_type=?, amount=?, description=? WHERE transactionID=?", tuple(data + [transactionID]))
        db.close()

        self.load_transactions()

    def delete_transaction(self):
        """Delete a selected transaction."""
        selected = self.transactions_listbox.get(self.transactions_listbox.curselection())
        if not selected:
            return

        transactionID = int(selected.split(":")[0])

        db = Database()
        db.query("DELETE FROM transactions WHERE transactionID=?", (transactionID,))
        db.close()

        self.load_transactions()


class PhysioApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Physiotherapy App')

        # Create buttons for each action
        self.appointments_button = tk.Button(self.root, text="Appointments", command=self.open_appointments)
        self.appointments_button.pack(pady=10)

        self.client_details_button = tk.Button(self.root, text="Client Details", command=self.open_client_details)
        self.client_details_button.pack(pady=10)

        self.staff_permissions_button = tk.Button(self.root, text="Staff Permissions", command=self.open_staff_permissions)
        self.staff_permissions_button.pack(pady=10)

        self.inventory_button = tk.Button(self.root, text="Inventory", command=self.open_inventory)
        self.inventory_button.pack(pady=10)

        self.transactions_button = tk.Button(self.root, text="Transactions", command=self.open_transactions)
        self.transactions_button.pack(pady=10)

    def open_appointments(self):
        self.open_window(AppointmentsWindow)

    def open_client_details(self):
        self.open_window(ClientDetailsWindow)

    def open_staff_permissions(self):
        self.open_window(StaffPermissionsWindow)

    def open_inventory(self):
        self.open_window(InventoryWindow)

    def open_transactions(self):
        self.open_window(TransactionsWindow)

    def open_window(self, window_class):
        new_window = tk.Toplevel(self.root)
        window_class(new_window)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x200")
    app = PhysioApp(root)
    root.mainloop()

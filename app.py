import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
import pandas as pd
import bcrypt
import re

class loginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        current_logged_in_user = None

        self.title("Login")
        self.geometry("300x300")

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(9, 9)
        ttk.Label(self, image=self.logo).pack(pady=5)

        frame = ttk.Frame(self)
        frame.pack(pady=20)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self, text="Login", command=self.login).pack(pady=5)

    def login(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')

        self.cursor.execute("SELECT password FROM login WHERE username=?", (username,))
        result = self.cursor.fetchone()

        if result and bcrypt.checkpw(password, result[0]):
            current_logged_in_user = username
            self.destroy()
            main_window = mainWindow()
            main_window.mainloop()

        else:
            messagebox.showerror("Error", "incorrect username or password!")

        self.conn.close()

class mainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Main Window")
        self.geometry("300x400")

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(6, 6)
        tk.Label(self, image=self.logo).pack(pady=5)

        ttk.Button(self, text="Appointments", command=self.open_appointments).pack(pady=5)
        ttk.Button(self, text="Clients", command=self.open_clients).pack(pady=5)
        ttk.Button(self, text="Staff", command=self.open_staff).pack(pady=5)
        ttk.Button(self, text="Transactions", command=self.WIP_window).pack(pady=5)
    
        button_logout = ttk.Button(self, text="Logout", command=self.logout).pack(pady=5)

    def logout(self):
        current_logged_in_user = None
        self.destroy()
        app = loginWindow()
        app.mainloop()

    def open_appointments(self):
        appointments_page(self)
    
    def open_clients(self):
        clients_page(self)

    def open_staff(self):
        staff_page(self)

    def WIP_window(self):
        pass

class appointments_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Appointments")
        self.geometry("600x600")

        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        self.appointments_table = ttk.Treeview(self, columns=('ID', 'Client Name', 'Staff Name', 'Service', 'Time & Date', 'Status'), show='headings', height=10)

        self.appointments_table.column('ID', width=30)
        self.appointments_table.column('Client Name', width=130)
        self.appointments_table.column('Staff Name', width=130)
        self.appointments_table.column('Service', width=75)
        self.appointments_table.column('Time & Date', width=100)
        self.appointments_table.column('Status', width=80)

        self.appointments_table.heading('ID', text='ID')
        self.appointments_table.heading('Client Name', text='Client Name')
        self.appointments_table.heading('Staff Name', text='Staff Name')
        self.appointments_table.heading('Service', text='Service')
        self.appointments_table.heading('Time & Date', text='Time & Date')
        self.appointments_table.heading('Status', text='Status')
        self.appointments_table.pack(pady=20)

        self.fetch_and_display()

        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        view_appointment = ttk.Button(menu_frame, text="View", command=self.view_appointment)
        view_appointment.grid(row=0, column=0, padx=5)

        add_appointment = ttk.Button(menu_frame, text="Add", command=self.add_appointment)
        add_appointment.grid(row=0, column=1, padx=5)

        edit_appointment = ttk.Button(menu_frame, text="Edit")
        edit_appointment.grid(row=0, column=2, padx=5)

        delete_appointment = ttk.Button(menu_frame, text="Delete", command=self.delete_appointment)
        delete_appointment.grid(row=0, column=3, padx=5)

        exportall_button = ttk.Button(menu_frame, text="Select All", command=self.select_all)
        exportall_button.grid(row=1, column=1, padx=5)

        export_button = ttk.Button(menu_frame, text="Export", command=self.export_selected)
        export_button.grid(row=1, column=2, padx=5)

        services_frame = ttk.Frame(self)
        services_frame.pack(pady=5)
        services_button = ttk.Button(services_frame, text="View and Edit services")
        services_button.pack(pady=10)

    def connect_database(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
        self.connect_database()
        query = '''
        SELECT
            appointment.appointment_id,
            client.client_forename || ' ' || client.client_surname AS client_name,
            staff.staff_forename || ' ' || staff.staff_surname AS staff_name,
            appointment.service_id,
            appointment.appointment_session_time || ' ' || appointment.appointment_session_date AS session_datetime,
            appointment.appointment_status,
            appointment.appointment_comments
        FROM
            appointment
            INNER JOIN client ON appointment.client_id = client.client_id
            INNER JOIN staff ON appointment.staff_id = staff.staff_id
        '''
        rows = self.cursor.execute(query).fetchall()
        
        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)
        
        for row in rows:
            self.appointments_table.insert('', 'end', values=row)
        
        self.conn.close()

    def view_appointment(self):
        selected_item = self.appointments_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an appointment to view.")
            return

        values = self.appointments_table.item(selected_item, 'values')

        appointment_id = values[0]

        self.connect_database()

        try:
            query = '''
            SELECT
                appointment.appointment_id,
                client.client_forename || ' ' || client.client_surname AS client_name,
                staff.staff_forename || ' ' || staff.staff_surname AS staff_name,
                appointment.service_id,
                appointment.appointment_session_time AS session_time,
                appointment.appointment_session_date AS session_date,
                appointment.appointment_status,
                appointment.appointment_comments
            FROM
                appointment
                INNER JOIN client ON appointment.client_id = client.client_id
                INNER JOIN staff ON appointment.staff_id = staff.staff_id
            WHERE
                appointment.appointment_id = ?
            '''
            row = self.cursor.execute(query, (appointment_id,)).fetchone()
            print(row)
            if not row:
                messagebox.showwarning("Warning", "The selected appointment was not found.")
                return
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()



    ### REWRITE OR SOMETHING IDK
    def search_name(self, clients_names):
        search_term = self.name_search_entry.get().lower()
        filtered_clients = [client for client in clients_names if search_term in f"{client[1]} {client[2]}".lower()]
        name_options = [f"{client[0]}, {client[1]} {client[2]}" for client in filtered_clients]
        menu = self.appointment_name_entry["menu"]
        menu.delete(0, "end")
        for option in name_options:
            menu.add_command(label=option, command=lambda value=option: self.name_selection.set(value))
    ### END OF REWRITE

    def add_appointment(self):
        self.add_appointment_window = tk.Toplevel(self)
        self.add_appointment_window.title("Add Appointment")
        self.add_appointment_window.geometry("400x300")

        add_appointment_frame = tk.Frame(self.add_appointment_window)
        add_appointment_frame.pack(padx=10, pady=10)

    ### GPT
        appointment_client_name_label = tk.Label(add_appointment_frame, text="*Client Name:")
        appointment_client_name_label.grid(row=0, column=0)
        self.name_selection = tk.StringVar()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT client_id, client_forename, client_surname FROM client")
        clients_names = cursor.fetchall()
        connection.close()
        name_options = [""] + [f"{client[0]}, {client[1]} {client[2]}" for client in clients_names]
        self.appointment_name_entry = ttk.OptionMenu(add_appointment_frame, self.name_selection, name_options[0], *name_options)
        self.appointment_name_entry.grid(row=0, column=1)

        self.name_search_entry = tk.Entry(add_appointment_frame)
        self.name_search_entry.grid(row=1, column=1)
        name_search_button = ttk.Button(add_appointment_frame, text="Search", command=lambda: self.search_name(clients_names))
        name_search_button.grid(row=1, column=2)
    ### GPT

        blank_label = tk.Label(add_appointment_frame, text="")
        blank_label.grid(row=2, column=0)
        
        #appointment_staff_name_label = tk.Label(add_appointment_frame, text="*Staff Member Assigned:")
        #appointment_staff_name_label.grid(row=3, column=0)
        #self.appointment_staff_name_entry = tk.Entry(add_appointment_frame)
        #self.appointment_staff_name_entry.grid(row=3, column=1)

        appointment_staff_name_label = tk.Label(add_appointment_frame, text="*Staff Member Assigned:")
        appointment_staff_name_label.grid(row=3, column=0)
        self.staff_name_selection = tk.StringVar()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT staff_id, staff_forename, staff_surname FROM staff WHERE staff_status = 'Currently Employed'")
        staff_names = cursor.fetchall()
        connection.close()
        staff_name_options = [""] + [f"{staff[0]}, {staff[1]} {staff[2]}" for staff in staff_names]
        self.appointment_staff_name_entry = ttk.OptionMenu(add_appointment_frame, self.staff_name_selection, staff_name_options[0], *staff_name_options)
        self.appointment_staff_name_entry.grid(row=3, column=1)

        self.appointment_service_selection = tk.StringVar()
        appointment_service_label = tk.Label(add_appointment_frame, text="*Service:")
        appointment_service_label.grid(row=4, column=0)
        service_options = ["", "legs", "arms", "back"]
        appointment_service_entry = ttk.OptionMenu(add_appointment_frame, self.appointment_service_selection, service_options[0], *service_options)
        appointment_service_entry.grid(row=4, column=1)

        self.name_search_entry = tk.Entry(add_appointment_frame)
        self.name_search_entry.grid(row=1, column=1)
        name_search_button = ttk.Button(add_appointment_frame, text="Search", command=lambda: self.search_name(clients_names))
        name_search_button.grid(row=1, column=2)

        appointment_time_label = tk.Label(add_appointment_frame, text="*24H Time in HH:MM")
        appointment_time_label.grid(row=5, column=0)
        self.appointment_time_entry = tk.Entry(add_appointment_frame)
        self.appointment_time_entry.grid(row=5, column=1)

        appointment_date_label = tk.Label(add_appointment_frame, text="*Date as [dd-mm-yyyy]")
        appointment_date_label.grid(row=6, column=0)
        self.appointment_date_entry = DateEntry(add_appointment_frame, date_pattern="dd-mm-yyyy", width=10)
        self.appointment_date_entry.grid(row=6, column=1)

        self.status_selection = tk.StringVar()
        appointment_status_label = tk.Label(add_appointment_frame, text="*Status:")
        appointment_status_label.grid(row=7, column=0)
        status_options = ["", "Upcoming", "Completed", "Cancelled"]
        self.appointment_status_entry = ttk.OptionMenu(add_appointment_frame, self.status_selection, status_options[0], *status_options)
        self.appointment_status_entry.grid(row=7, column=1)

        appointment_comment_label = tk.Label(add_appointment_frame, text="Comment")
        appointment_comment_label.grid(row=8, column=0)
        self.appointment_comment_entry = tk.Entry(add_appointment_frame)
        self.appointment_comment_entry.grid(row=8, column=1)

        submit_button = ttk.Button(add_appointment_frame, text="Add New Appointment", command=self.submit_appointment)
        submit_button.grid(row=9, column=0, columnspan=2)

    def submit_appointment(self):
        client_name = self.name_selection.get()
        staff_name = self.staff_name_selection.get()
        service_name = self.appointment_service_selection.get()
        time = self.appointment_time_entry.get()
        date = self.appointment_date_entry.get()
        status = self.status_selection.get()
        comment = self.appointment_comment_entry.get()

        if not client_name or not staff_name or not service_name or not time or not date or not status:
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        try:
            client_id = int(client_name.split(",")[0])
            staff_id = int(staff_name.split(",")[0])

            cursor.execute('''
                INSERT INTO appointment (client_id, staff_id, service_id, appointment_session_time, appointment_session_date, appointment_status, appointment_comments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, staff_id, service_name, time, date, status, comment))

            connection.commit()
            connection.close()
            messagebox.showinfo("Info", "Appointment added successfully!")
            self.add_appointment_window.destroy()
            self.fetch_and_display()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    ### check that this finally is present in other areas of my code
        finally:
            if connection:
                connection.close()
    ###

    def delete_appointment(self):
        selected_items = self.appointments_table.selection()

        if not selected_items:
            messagebox.showwarning("Warning", "Please select appointment(s) to delete.")
            return

        number_selected = len(selected_items)
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} appointment(s)?")
        if not confirm:
            return

        self.connect_database()

        try:
            for item in selected_items:
                appointment_id = self.appointments_table.item(item, 'values')[0]
                self.cursor.execute("DELETE FROM appointment WHERE appointment_id=?", (appointment_id,))
                self.appointments_table.delete(item)

            self.conn.commit()
            messagebox.showinfo("Info", "Appointment(s) deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def select_all(self):
        items = self.appointments_table.get_children()
        for item in items:
            self.appointments_table.selection_add(item)

    def export_selected(self):
        selected_items = self.appointments_table.selection()

        if not selected_items:
            messagebox.showwarning("Warning", "No appointments selected for export.")
            return

        self.connect_database()

        try:
            appointment_data = []
            for item in selected_items:
                # Extract the appointment_id from the item ID
                appointment_id = self.appointments_table.item(item, 'values')[0]
                row = self.cursor.execute("SELECT * FROM appointment WHERE appointment_id=?", (appointment_id,)).fetchone()
                if row:
                    appointment_data.append(row)

            if appointment_data:
                columns = ["appointment_id", "client_id", "staff_id", "service_id", "appointment_session_time", "appointment_session_date", "appointment_status", "appointment_comments"]
                df = pd.DataFrame(appointment_data, columns=columns)

                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Info", "Selected appointment(s) exported to Excel successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()


class clients_page(tk.Toplevel):

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Clients")
        self.geometry("550x600")

        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        self.client_table = ttk.Treeview(self, columns=('ID', 'Name', 'DOB', 'Gender', 'Email', 'Phone'), show='headings', height=14)

        self.client_table.column('ID', width=30)
        self.client_table.column('Name', width=120)
        self.client_table.column('DOB', width=70)
        self.client_table.column('Gender', width=50)
        self.client_table.column('Email', width=150)
        self.client_table.column('Phone', width=75)

        self.client_table.heading('ID', text='ID')
        self.client_table.heading('Name', text='Name')
        self.client_table.heading('DOB', text='DOB')
        self.client_table.heading('Gender', text='Gender')
        self.client_table.heading('Email', text='Email')
        self.client_table.heading('Phone', text='Phone')
        self.client_table.pack(pady=20)

        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        view_client = ttk.Button(menu_frame, text="View", command=self.view_client)
        view_client.grid(row=0, column=0, padx=5)

        add_client = ttk.Button(menu_frame, text="Add", command=self.add_client)
        add_client.grid(row=0, column=1, padx=5)

        edit_client = ttk.Button(menu_frame, text="Edit", command=self.edit_client)
        edit_client.grid(row=0, column=2, padx=5)

        delete_client = ttk.Button(menu_frame, text="Delete", command=self.delete_client)
        delete_client.grid(row=0, column=3, padx=5)

        select_all_button = ttk.Button(menu_frame, text="Select All", command=self.select_all)
        select_all_button.grid(row=2, column=1, padx=5, pady=10)

        export_button = ttk.Button(menu_frame, text="Export Selected", command=self.export_selected)
        export_button.grid(row=2, column=2, padx=5, pady=10)

        self.fetch_and_display()

    def connect_database(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
        self.connect_database()
        query = '''
        SELECT client_id, client_forename || ' ' || client_surname AS Name, client_DOB AS DOB, client_gender AS Gender, client_email AS Email, client_phone as Phone
        FROM client
        ORDER BY Name
        '''
        rows = self.cursor.execute(query).fetchall()
        for row in rows:
            self.client_table.insert("", "end", iid=row[0], values=row) 

    def view_client(self):
        selected_item = self.client_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a client to view.")
            return

        client_id = selected_item[0]
        self.connect_database()

        try:
            row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
            if not row:
                messagebox.showwarning("Warning", "The selected client was not found.")
                return

            self.view_client_window = tk.Toplevel(self)
            self.view_client_window.title("View Client")
            self.view_client_window.geometry("300x300")

            view_client_frame = tk.Frame(self.view_client_window)
            view_client_frame.pack(padx=10, pady=10)

            client_forename_label = tk.Label(view_client_frame, text="Client ID: " + str(row[0]))
            client_forename_label.grid(row=0, column=0)

            client_forename_label = tk.Label(view_client_frame, text="Forename: " + row[1])
            client_forename_label.grid(row=1, column=0)

            client_surname_label = tk.Label(view_client_frame, text="Surname: " + row[2])
            client_surname_label.grid(row=2, column=0)

            client_dob_label = tk.Label(view_client_frame, text="DOB: " + row[3])
            client_dob_label.grid(row=3, column=0)

            client_gender_label = tk.Label(view_client_frame, text="Gender: " + row[4])
            client_gender_label.grid(row=4, column=0)

            client_phone_label = tk.Label(view_client_frame, text="Phone: " + row[5])
            client_phone_label.grid(row=5, column=0)

            client_email_label = tk.Label(view_client_frame, text="Email: " + row[6])
            client_email_label.grid(row=6, column=0)

            client_address_label = tk.Label(view_client_frame, text="Address: " + row[7])
            client_address_label.grid(row=7, column=0)

            client_comments_label = tk.Label(view_client_frame, text="Comments: " + row[8])
            client_comments_label.grid(row=8, column=0)
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def add_client(self):
        self.add_client_window = tk.Toplevel(self)
        self.add_client_window.title("Add Client")
        self.add_client_window.geometry("300x300")

        add_client_frame = tk.Frame(self.add_client_window)
        add_client_frame.pack(padx=10, pady=10)

        client_forename_label = tk.Label(add_client_frame, text="*Forename:")
        client_forename_label.grid(row=0, column=0)
        self.client_forename_entry = tk.Entry(add_client_frame)
        self.client_forename_entry.grid(row=0, column=1)
        
        client_surname_label = tk.Label(add_client_frame, text="*Surname:")
        client_surname_label.grid(row=1, column=0)
        self.client_surname_entry = tk.Entry(add_client_frame)
        self.client_surname_entry.grid(row=1, column=1)
        
        client_dob_label = tk.Label(add_client_frame, text="*DOB:")
        client_dob_label.grid(row=2, column=0)
        self.client_dob_entry = tk.Entry(add_client_frame)
        self.client_dob_entry.grid(row=2, column=1)

        self.gender_selection = tk.StringVar()
        client_gender_label = tk.Label(add_client_frame, text="*Gender:")
        client_gender_label.grid(row=3, column=0)
        gender_options = ["", "Male", "Female", "Other"]
        gender_entry = ttk.OptionMenu(add_client_frame, self.gender_selection, gender_options[0], *gender_options)
        gender_entry.grid(row=3, column=1)

        client_phone_label = tk.Label(add_client_frame, text="(*)Phone:")
        client_phone_label.grid(row=4, column=0)
        self.client_phone_entry = tk.Entry(add_client_frame)
        self.client_phone_entry.grid(row=4, column=1)
        
        client_email_label = tk.Label(add_client_frame, text="(*)Email:")
        client_email_label.grid(row=5, column=0)
        self.client_email_entry = tk.Entry(add_client_frame)
        self.client_email_entry.grid(row=5, column=1)

        client_address_label = tk.Label(add_client_frame, text="Address:")
        client_address_label.grid(row=6, column=0)
        self.client_address_entry = tk.Entry(add_client_frame)
        self.client_address_entry.grid(row=6, column=1)

        client_comments_label = tk.Label(add_client_frame, text="Comments:")
        client_comments_label.grid(row=8, column=0)
        self.client_comments_entry = tk.Entry(add_client_frame)
        self.client_comments_entry.grid(row=8, column=1)

        submit_button = ttk.Button(add_client_frame, text="Add New Client", command=self.submit_user)
        submit_button.grid(row=9, column=0, columnspan=2)

    def submit_user(self):
        forename = self.client_forename_entry.get()
        surname = self.client_surname_entry.get()
        DOB = self.client_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        address = self.client_address_entry.get()
        comments = self.client_comments_entry.get()

        if not forename or not surname or not DOB or not gender:
            messagebox.showerror("Error", "Fields marked with * are required!")
            return
        
        if not (phone or email):
            messagebox.showerror("Error", "Either a phone number or an email address is required!")
            return

        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        if phone and not phone.isdigit():
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            self.connect_database()
            self.cursor.execute("INSERT INTO client (client_forename, client_surname, client_DOB, client_gender, client_phone, client_email, client_address, client_comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (forename, surname, DOB, gender, phone, email, address, comments))
            self.conn.commit()

            for row in self.client_table.get_children():
                self.client_table.delete(row)
            self.fetch_and_display()

            self.add_client_window.destroy()

            messagebox.showinfo("Info", "Client added successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def edit_client(self):
        selected_items = self.client_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a client to edit.")
        elif len(selected_items) > 1:
            messagebox.showwarning("Warning", "Multiple items selected, please only select one to edit.")
        else:
            client_id = selected_items[0]
            self.connect_database()

            try:
                row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
                if not row:
                    messagebox.showwarning("Warning", "The selected client was not found.")
                else:
                    self.edit_client_window = tk.Toplevel(self)
                    self.edit_client_window.title("Edit Client")
                    self.edit_client_window.geometry("300x300")

                    edit_client_frame = tk.Frame(self.edit_client_window)
                    edit_client_frame.pack(padx=10, pady=10)

                    client_forename_label = tk.Label(edit_client_frame, text="*Forename:")
                    client_forename_label.grid(row=0, column=0)
                    self.client_forename_entry = tk.Entry(edit_client_frame)
                    self.client_forename_entry.grid(row=0, column=1)
                    self.client_forename_entry.insert(0, row[1])

                    client_surname_label = tk.Label(edit_client_frame, text="*Surname:")
                    client_surname_label.grid(row=1, column=0)
                    self.client_surname_entry = tk.Entry(edit_client_frame)
                    self.client_surname_entry.grid(row=1, column=1)
                    self.client_surname_entry.insert(0, row[2])

                    client_dob_label = tk.Label(edit_client_frame, text="*DOB:")
                    client_dob_label.grid(row=2, column=0)
                    self.client_dob_entry = tk.Entry(edit_client_frame)
                    self.client_dob_entry.grid(row=2, column=1)
                    self.client_dob_entry.insert(0, row[3])

                    self.gender_selection = tk.StringVar()
                    client_gender_label = tk.Label(edit_client_frame, text="*Gender:")
                    client_gender_label.grid(row=3, column=0)
                    gender_options = ["", "Male", "Female", "Other"]
                    selected_gender = row[4]
                    gender_selection = tk.StringVar(value=selected_gender)
                    client_gender_entry = ttk.OptionMenu(edit_client_frame, self.gender_selection, selected_gender, *gender_options)
                    client_gender_entry.grid(row=3, column=1)

                    client_phone_label = tk.Label(edit_client_frame, text="Phone:")
                    client_phone_label.grid(row=4, column=0)
                    self.client_phone_entry = tk.Entry(edit_client_frame)
                    self.client_phone_entry.grid(row=4, column=1)
                    self.client_phone_entry.insert(0, row[5])

                    client_email_label = tk.Label(edit_client_frame, text="Email:")
                    client_email_label.grid(row=5, column=0)
                    self.client_email_entry = tk.Entry(edit_client_frame)
                    self.client_email_entry.grid(row=5, column=1)
                    self.client_email_entry.insert(0, row[6])

                    client_address_label = tk.Label(edit_client_frame, text="Address:")
                    client_address_label.grid(row=6, column=0)
                    self.client_address_entry = tk.Entry(edit_client_frame)
                    self.client_address_entry.grid(row=6, column=1)
                    self.client_address_entry.insert(0, row[7])

                    client_comments_label = tk.Label(edit_client_frame, text="Comments:")
                    client_comments_label.grid(row=8, column=0)
                    self.client_comments_entry = tk.Entry(edit_client_frame)
                    self.client_comments_entry.grid(row=8, column=1)
                    self.client_comments_entry.insert(0, row[8])

                    submit_button = ttk.Button(edit_client_frame, text="Update Client", command=lambda: self.update_user(row[0]))
                    submit_button.grid(row=9, column=0, columnspan=2)

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                self.conn.close()

    def update_user(self, client_id):
        forename = self.client_forename_entry.get()
        surname = self.client_surname_entry.get()
        DOB = self.client_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        address = self.client_address_entry.get()
        comments = self.client_comments_entry.get()

        if not forename or not surname or not DOB or not gender:
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        if phone and not phone.isdigit():
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            self.connect_database()
            self.cursor.execute("""
                UPDATE client 
                SET client_forename=?, client_surname=?, client_DOB=?, client_gender=?, client_phone=?, client_email=?, client_address=?, client_comments=? 
                WHERE client_id=?
            """, (forename, surname, DOB, gender, phone, email, address, comments, client_id))


            self.conn.commit()

            for row in self.client_table.get_children():
                self.client_table.delete(row)
            self.fetch_and_display()

            self.edit_client_window.destroy()
            messagebox.showinfo("Info", "Client updated successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def delete_client(self):
        selected_items = self.client_table.selection()

        if not selected_items:
            messagebox.showwarning("Warning", "Please select a client to delete.")
            return

        number_selected = len(selected_items)
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} client(s)?")
        if not confirm:
            return

        self.connect_database()

        try:
            for client_id in selected_items:
                self.cursor.execute("DELETE FROM client WHERE client_id=?", (client_id,))
                self.client_table.delete(client_id)

            self.conn.commit()
            messagebox.showinfo("Info", "Clients deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def select_all(self):
        items = self.client_table.get_children()
        for item in items:
            self.client_table.selection_add(item)

    def export_selected(self):
        selected_items = self.client_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No clients selected for export.")
            return
        
        self.connect_database()

        try:
            client_data = []
            for client_id in selected_items:
                row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
                if row:
                    client_data.append(row)

    ### rewrite this code to be in own writing
            if client_data:
                df = pd.DataFrame(client_data, columns=["client_id", "client_forename", "client_surname", "client_DOB", "client_gender", "client_phone", "client_email", "client_address", "client_comments"])

                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Info", "Selected clients exported to Excel successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()
    ### end of rewrite code

class staff_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Staff")
        self.geometry("500x600")

        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        self.staff_table = ttk.Treeview(self, columns=('Name', 'Gender', 'DOB', 'Status'), show='headings', height=14)

        self.staff_table.column('Name', width=170)
        self.staff_table.column('Gender', width=50)
        self.staff_table.column('DOB', width=70)
        self.staff_table.column('Status', width=120)

        self.staff_table.heading('Name', text='Name')
        self.staff_table.heading('Gender', text='Gender')
        self.staff_table.heading('DOB', text='DOB')
        self.staff_table.heading('Status', text='Status')
        self.staff_table.pack(pady=20)

        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        view_staff = ttk.Button(menu_frame, text="View", command=self.view_staff_member)
        view_staff.grid(row=0, column=0, padx=5)

        add_staff = ttk.Button(menu_frame, text="Add", command=self.add_staff_member)
        add_staff.grid(row=0, column=1, padx=5)

        edit_staff = ttk.Button(menu_frame, text="Edit", command=self.edit_staff_member)
        edit_staff.grid(row=0, column=2, padx=5)

        delete_staff = ttk.Button(menu_frame, text="Delete", command=self.delete_staff_member)
        delete_staff.grid(row=0, column=3, padx=5)

        select_all_button = ttk.Button(menu_frame, text="Select All", command=self.select_all)
        select_all_button.grid(row=2, column=1, padx=5, pady=10)

        export_button = ttk.Button(menu_frame, text="Export Selected", command=self.export_selected)
        export_button.grid(row=2, column=2, padx=5, pady=10)

        self.fetch_and_display()

    def connect_database(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
    ### Make this either more complex or make this somehow better 30/10/23
    ### Maybe change the || ' ' || to something more clear?
        self.connect_database()
        query = '''
        SELECT staff_id, staff_forename || ' ' || staff_surname AS Name, staff_gender AS Gender, staff_DOB AS DOB, staff_status AS Status
        FROM staff
        ORDER BY Name
        '''
        rows = self.cursor.execute(query).fetchall()
        for row in rows:
            self.staff_table.insert("", "end", iid=row[0], values=row[1:])  

    def view_staff_member(self):
        selected_item = self.staff_table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a staff member to view.")
            return

        staff_id = selected_item[0]
        self.connect_database()

        try:
            row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
            if not row:
                messagebox.showwarning("Warning", "The selected staff member was not found.")
                return

            self.view_staff_window = tk.Toplevel(self)
            self.view_staff_window.title("View Staff Member")
            self.view_staff_window.geometry("300x300")

            view_staff_frame = tk.Frame(self.view_staff_window)
            view_staff_frame.pack(padx=10, pady=10)

            staff_forename_label = tk.Label(view_staff_frame, text="Staff ID: " + str(row[0]))
            staff_forename_label.grid(row=0, column=0)

            staff_forename_label = tk.Label(view_staff_frame, text="Forename: " + row[1])
            staff_forename_label.grid(row=1, column=0)

            staff_surname_label = tk.Label(view_staff_frame, text="Surname: " + row[2])
            staff_surname_label.grid(row=2, column=0)

            staff_dob_label = tk.Label(view_staff_frame, text="DOB: " + row[3])
            staff_dob_label.grid(row=3, column=0)

            staff_gender_label = tk.Label(view_staff_frame, text="Gender: " + row[4])
            staff_gender_label.grid(row=4, column=0)

            staff_phone_label = tk.Label(view_staff_frame, text="Phone: " + row[5])
            staff_phone_label.grid(row=5, column=0)

            staff_email_label = tk.Label(view_staff_frame, text="Email: " + row[6])
            staff_email_label.grid(row=6, column=0)

            staff_address_label = tk.Label(view_staff_frame, text="Address: " + row[7])
            staff_address_label.grid(row=7, column=0)

            staff_status_label = tk.Label(view_staff_frame, text="Status: " + row[8])
            staff_status_label.grid(row=8, column=0)

            staff_comments_label = tk.Label(view_staff_frame, text="Comments: " + row[9])
            staff_comments_label.grid(row=9, column=0)
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def add_staff_member(self):
        self.add_staff_window = tk.Toplevel(self)
        self.add_staff_window.title("Add Staff Member")
        self.add_staff_window.geometry("300x300")

        add_staff_frame = tk.Frame(self.add_staff_window)
        add_staff_frame.pack(padx=10, pady=10)

        staff_forename_label = tk.Label(add_staff_frame, text="*Forename:")
        staff_forename_label.grid(row=0, column=0)
        self.staff_forename_entry = tk.Entry(add_staff_frame)
        self.staff_forename_entry.grid(row=0, column=1)
        
        staff_surname_label = tk.Label(add_staff_frame, text="*Surname:")
        staff_surname_label.grid(row=1, column=0)
        self.staff_surname_entry = tk.Entry(add_staff_frame)
        self.staff_surname_entry.grid(row=1, column=1)
        
        staff_dob_label = tk.Label(add_staff_frame, text="*DOB:")
        staff_dob_label.grid(row=2, column=0)
        self.staff_dob_entry = tk.Entry(add_staff_frame)
        self.staff_dob_entry.grid(row=2, column=1)

        self.gender_selection = tk.StringVar()
        staff_gender_label = tk.Label(add_staff_frame, text="*Gender:")
        staff_gender_label.grid(row=3, column=0)
        gender_options = ["", "Male", "Female", "Other"]
        gender_entry = ttk.OptionMenu(add_staff_frame, self.gender_selection, gender_options[0], *gender_options)
        gender_entry.grid(row=3, column=1)

        staff_phone_label = tk.Label(add_staff_frame, text="Phone:")
        staff_phone_label.grid(row=4, column=0)
        self.staff_phone_entry = tk.Entry(add_staff_frame)
        self.staff_phone_entry.grid(row=4, column=1)
        
        staff_email_label = tk.Label(add_staff_frame, text="Email:")
        staff_email_label.grid(row=5, column=0)
        self.staff_email_entry = tk.Entry(add_staff_frame)
        self.staff_email_entry.grid(row=5, column=1)

        staff_address_label = tk.Label(add_staff_frame, text="Address:")
        staff_address_label.grid(row=6, column=0)
        self.staff_address_entry = tk.Entry(add_staff_frame)
        self.staff_address_entry.grid(row=6, column=1)

        self.status_selection = tk.StringVar()
        staff_status_label = tk.Label(add_staff_frame, text="*Status:")
        staff_status_label.grid(row=7, column=0)
        status_options = ["Currently Employed", "Previously Employed", "Not Employed", "Other"]
        self.status_entry = ttk.OptionMenu(add_staff_frame, self.status_selection, status_options[0], *status_options)
        self.status_entry.grid(row=7, column=1)

        staff_comments_label = tk.Label(add_staff_frame, text="Comments:")
        staff_comments_label.grid(row=8, column=0)
        self.staff_comments_entry = tk.Entry(add_staff_frame)
        self.staff_comments_entry.grid(row=8, column=1)

        submit_button = ttk.Button(add_staff_frame, text="Add New Staff Member", command=self.submit_user)
        submit_button.grid(row=9, column=0, columnspan=2)

    def submit_user(self):
        forename = self.staff_forename_entry.get()
        surname = self.staff_surname_entry.get()
        DOB = self.staff_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.staff_phone_entry.get()
        email = self.staff_email_entry.get()
        address = self.staff_address_entry.get()
        status = self.status_selection.get()
        comments = self.staff_comments_entry.get()

        if not forename or not surname or not DOB or not gender or not status:
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        if phone and not phone.isdigit():
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            self.connect_database()
            self.cursor.execute("INSERT INTO staff (staff_forename, staff_surname, staff_DOB, staff_gender, staff_phone, staff_email, staff_address, staff_status, staff_comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (forename, surname, DOB, gender, phone, email, address, status, comments))
            self.conn.commit()

            for row in self.staff_table.get_children():
                self.staff_table.delete(row)
            self.fetch_and_display()

            self.add_staff_window.destroy()

            messagebox.showinfo("Info", "Staff member added successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def edit_staff_member(self):
        selected_items = self.staff_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a staff member to edit.")
        elif len(selected_items) > 1:
            messagebox.showwarning("Warning", "Multiple items selected, please only select one to edit.")
        else:
            staff_id = selected_items[0]
            self.connect_database()

            try:
                row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
                if not row:
                    messagebox.showwarning("Warning", "The selected staff member was not found.")
                else:
                    self.edit_staff_window = tk.Toplevel(self)
                    self.edit_staff_window.title("Edit Staff Member")
                    self.edit_staff_window.geometry("300x300")

                    edit_staff_frame = tk.Frame(self.edit_staff_window)
                    edit_staff_frame.pack(padx=10, pady=10)

                    staff_forename_label = tk.Label(edit_staff_frame, text="*Forename:")
                    staff_forename_label.grid(row=0, column=0)
                    self.staff_forename_entry = tk.Entry(edit_staff_frame)
                    self.staff_forename_entry.grid(row=0, column=1)
                    self.staff_forename_entry.insert(0, row[1])

                    staff_surname_label = tk.Label(edit_staff_frame, text="*Surname:")
                    staff_surname_label.grid(row=1, column=0)
                    self.staff_surname_entry = tk.Entry(edit_staff_frame)
                    self.staff_surname_entry.grid(row=1, column=1)
                    self.staff_surname_entry.insert(0, row[2])

                    staff_dob_label = tk.Label(edit_staff_frame, text="*DOB:")
                    staff_dob_label.grid(row=2, column=0)
                    self.staff_dob_entry = tk.Entry(edit_staff_frame)
                    self.staff_dob_entry.grid(row=2, column=1)
                    self.staff_dob_entry.insert(0, row[3])

                    self.gender_selection = tk.StringVar()
                    staff_gender_label = tk.Label(edit_staff_frame, text="*Gender:")
                    staff_gender_label.grid(row=3, column=0)
                    gender_options = ["", "Male", "Female", "Other"]
                    selected_gender = row[4]
                    gender_selection = tk.StringVar(value=selected_gender)
                    staff_gender_entry = ttk.OptionMenu(edit_staff_frame, self.gender_selection, selected_gender, *gender_options)
                    staff_gender_entry.grid(row=3, column=1)
                    

                    staff_phone_label = tk.Label(edit_staff_frame, text="Phone:")
                    staff_phone_label.grid(row=4, column=0)
                    self.staff_phone_entry = tk.Entry(edit_staff_frame)
                    self.staff_phone_entry.grid(row=4, column=1)
                    self.staff_phone_entry.insert(0, row[5])

                    staff_email_label = tk.Label(edit_staff_frame, text="Email:")
                    staff_email_label.grid(row=5, column=0)
                    self.staff_email_entry = tk.Entry(edit_staff_frame)
                    self.staff_email_entry.grid(row=5, column=1)
                    self.staff_email_entry.insert(0, row[6])

                    staff_address_label = tk.Label(edit_staff_frame, text="Address:")
                    staff_address_label.grid(row=6, column=0)
                    self.staff_address_entry = tk.Entry(edit_staff_frame)
                    self.staff_address_entry.grid(row=6, column=1)
                    self.staff_address_entry.insert(0, row[7])

                    self.status_selection = tk.StringVar()
                    staff_status_label = tk.Label(edit_staff_frame, text="*Status:")
                    staff_status_label.grid(row=7, column=0)
                    status_options = ["Currently Employed", "Previously Employed", "Not Employed", "Other"]
                    selected_status = row[8]
                    status_selection = tk.StringVar(value=selected_status)
                    staff_status_entry = ttk.OptionMenu(edit_staff_frame, self.status_selection, selected_status, *status_options)
                    staff_status_entry.grid(row=7, column=1)

                    staff_comments_label = tk.Label(edit_staff_frame, text="Comments:")
                    staff_comments_label.grid(row=8, column=0)
                    self.staff_comments_entry = tk.Entry(edit_staff_frame)
                    self.staff_comments_entry.grid(row=8, column=1)
                    self.staff_comments_entry.insert(0, row[9])

                    submit_button = ttk.Button(edit_staff_frame, text="Update Staff Member", command=lambda: self.update_user(row[0]))
                    submit_button.grid(row=9, column=0, columnspan=2)

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                self.conn.close()

    def update_user(self, staff_id):
        forename = self.staff_forename_entry.get()
        surname = self.staff_surname_entry.get()
        DOB = self.staff_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.staff_phone_entry.get()
        email = self.staff_email_entry.get()
        address = self.staff_address_entry.get()
        status = self.status_selection.get()
        comments = self.staff_comments_entry.get()

        print(forename, surname, DOB, gender, phone, email, address, status, comments)

        if not forename or not surname or not DOB or not gender or not status:
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        if phone and not phone.isdigit():
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            self.connect_database()
            self.cursor.execute("""
                UPDATE staff 
                SET staff_forename=?, staff_surname=?, staff_DOB=?, staff_gender=?, staff_phone=?, staff_email=?, staff_address=?, staff_status=?, staff_comments=? 
                WHERE staff_id=?
            """, (forename, surname, DOB, gender, phone, email, address, status, comments, staff_id))


            self.conn.commit()

            for row in self.staff_table.get_children():
                self.staff_table.delete(row)
            self.fetch_and_display()

            self.edit_staff_window.destroy()
            messagebox.showinfo("Info", "Staff member updated successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def delete_staff_member(self):
        selected_items = self.staff_table.selection()

        if not selected_items:
            messagebox.showwarning("Warning", "Please select staff members to delete.")
            return

        number_selected = len(selected_items)
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} staff member(s)?")
        if not confirm:
            return

        self.connect_database()

        try:
            for staff_id in selected_items:
                self.cursor.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
                self.staff_table.delete(staff_id)

            self.conn.commit()
            messagebox.showinfo("Info", "Staff members deleted successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()

    def select_all(self):
        items = self.staff_table.get_children()
        for item in items:
            self.staff_table.selection_add(item)

    def export_selected(self):
        selected_items = self.staff_table.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No staff members selected for export.")
            return
        
        self.connect_database()

        try:
            staff_data = []
            for staff_id in selected_items:
                row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
                if row:
                    staff_data.append(row)

    ### rewrite this code to be in own writing
            if staff_data:
                df = pd.DataFrame(staff_data, columns=["staff_id", "staff_forename", "staff_surname", "staff_DOB", "staff_gender", "staff_phone", "staff_email", "staff_address", "staff_status", "staff_comments"])

                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    df.to_excel(file_path, index=False)
                    messagebox.showinfo("Info", "Selected staff members exported to Excel successfully!")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.conn.close()
    ### end of rewrite code

if __name__ == "__main__":
    app = loginWindow()
    app.mainloop()
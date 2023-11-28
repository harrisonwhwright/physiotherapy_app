import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkcalendar import DateEntry
import sqlite3
import pandas as pd
import bcrypt
import re

# This class displays the login window and handles all functions of logging in
class loginWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Initialise a variable to track the current logged-in user
        current_logged_in_user = None

        # Set up the login window
        self.title("Login")
        self.geometry("300x300")

        # Display logo
        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(9, 9)
        ttk.Label(self, image=self.logo).pack(pady=5)

        # Create a frame to place the username and password entry boxes
        frame = ttk.Frame(self)
        frame.pack(pady=20)

        # Username entry
        ttk.Label(frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Password entry
        ttk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Login Button
        ttk.Button(self, text="Login", command=self.login).pack(pady=5)

    def login(self):
        # Connect to the database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

        # Retrive the username and password from the entry boxes
        username = self.username_entry.get()
        password = self.password_entry.get().encode('utf-8')

        # Search the database and retrieve the password where the usernames match
        self.cursor.execute("SELECT password FROM login WHERE username=?", (username,))
        result = self.cursor.fetchone()

        # Check to make sure that the password matches the one found in the database
        if result and bcrypt.checkpw(password, result[0]):
            # If successful login, then assign the current logged in user
            current_logged_in_user = username
            self.destroy()
            # Load up the main window for the program
            main_window = mainWindow()
            main_window.mainloop()

        else:
            # Display an error message if the username and associated password do not match
            messagebox.showerror("Error", "incorrect username or password!")

        # Close the database connection
        self.conn.close()

# This class displays the main window and allows for navigation between the program's windows
class mainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.title("Main Window")
        self.geometry("300x400")

        # Display logo
        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(6, 6)
        tk.Label(self, image=self.logo).pack(pady=5)

        # Display all the buttons to allow for navigation between the program
        ttk.Button(self, text="Appointments", command=self.open_appointments).pack(pady=5)
        ttk.Button(self, text="Clients", command=self.open_clients).pack(pady=5)
        ttk.Button(self, text="Staff", command=self.open_staff).pack(pady=5)
        ttk.Button(self, text="Transactions", command=self.open_transactions).pack(pady=5)
    
        # Display the button that allows the user to log out
        button_logout = ttk.Button(self, text="Logout", command=self.logout).pack(pady=5)

    def logout(self):
        # Reset the current loggin-in user, then returns back to the login window
        current_logged_in_user = None
        self.destroy()
        app = loginWindow()
        app.mainloop()

    def open_appointments(self):
        # Open the appointemnts page
        appointments_page(self)
    
    def open_clients(self):
        # Open the clients page
        clients_page(self)

    def open_staff(self):
        # Open the staff page
        staff_page(self)

    def open_transactions(self):
        # Open the transactions page
        pass

# This class allows the user to create and interact with all stored appointents
class appointments_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        # Set up the appointments window
        self.title("Appointments")
        self.geometry("600x600")

        # Create a heading frame to display the logo
        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)
        # Display logo
        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        # Create the appointments display table
        self.appointments_table = ttk.Treeview(self, columns=('ID', 'Client Name', 'Staff Name', 'Service', 'Time & Date', 'Status'), show='headings', height=10)

        # Create columns to the display table
        self.appointments_table.column('ID', width=30)
        self.appointments_table.column('Client Name', width=130)
        self.appointments_table.column('Staff Name', width=130)
        self.appointments_table.column('Service', width=75)
        self.appointments_table.column('Time & Date', width=100)
        self.appointments_table.column('Status', width=80)

        # Give each column a heading in the display table
        self.appointments_table.heading('ID', text='ID')
        self.appointments_table.heading('Client Name', text='Client Name')
        self.appointments_table.heading('Staff Name', text='Staff Name')
        self.appointments_table.heading('Service', text='Service')
        self.appointments_table.heading('Time & Date', text='Time & Date')
        self.appointments_table.heading('Status', text='Status')
        self.appointments_table.pack(pady=20)

        # Fetch and display the appointments from the database
        self.fetch_and_display()

        # Create the menu frame to display the buttons
        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        # Create and display the buttons
        view_appointment = ttk.Button(menu_frame, text="View", command=self.view_appointment)
        view_appointment.grid(row=0, column=0, padx=5)

        add_appointment = ttk.Button(menu_frame, text="Add", command=self.add_appointment)
        add_appointment.grid(row=0, column=1, padx=5)

        edit_appointment = ttk.Button(menu_frame, text="Edit", command=self.edit_appointment)
        edit_appointment.grid(row=0, column=2, padx=5)

        delete_appointment = ttk.Button(menu_frame, text="Delete", command=self.delete_appointment)
        delete_appointment.grid(row=0, column=3, padx=5)

        exportall_button = ttk.Button(menu_frame, text="Select All", command=self.select_all)
        exportall_button.grid(row=1, column=1, padx=5)

        export_button = ttk.Button(menu_frame, text="Export", command=self.export_selected)
        export_button.grid(row=1, column=2, padx=5)

        # Create a frame and display a button to access the services page
        services_frame = ttk.Frame(self)
        services_frame.pack(pady=5)
        services_button = ttk.Button(services_frame, text="View and Edit services")
        services_button.pack(pady=10)

    def connect_database(self):
        # Establish a connection to the database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
        # Fetch appointments from the database and then display them in the table
        self.connect_database()
        # Take the IDs stored in the appointents table and search the database
        # This is done to retrieve the relevant inforamtion about the clients, staff, etc.
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
        # Retrieve every item from the appointment database 
        rows = self.cursor.execute(query).fetchall()
        
        # Clear the existing rows in the display table
        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)
        
        # Insert the rows from the database into the display table
        for row in rows:
            self.appointments_table.insert('', 'end', values=row)
        
        # Close the database
        self.conn.close()

    def view_appointment(self):
        # Retrieve the item that the user has selected
        selected_item = self.appointments_table.selection()
        if not selected_item:
            # If no item has been selected then display a warning
            messagebox.showwarning("Warning", "Please select an appointment to view.")
            return

        # Gets the appointment ID from the selected row
        values = self.appointments_table.item(selected_item, 'values')
        appointment_id = values[0]
        # Connect to the database
        self.connect_database()

        try:
            # Retrieve the appointment details for the selected ID
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
            if not row:
                # If no row is found then display a warning
                messagebox.showwarning("Warning", "The selected appointment was not found.")
                return
        except sqlite3.Error as e:
            # If there is an error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def search_name(self, clients_names):
        # Get the search term from the entery box
        # Standardise by setting it to lowercase
        search_term = self.name_search_entry.get().lower()
        # Filter the clients based on the search term in their names
        # Then create a list of names for the list
        filtered_clients = [client for client in clients_names if search_term in f"{client[1]} {client[2]}".lower()]
        name_options = [f"{client[0]}, {client[1]} {client[2]}" for client in filtered_clients]
        # Get the menu associated with the entry widget and clear the options
        # Then add the new options to the list based on what the user entered
        menu = self.appointment_name_entry["menu"]
        menu.delete(0, "end")
        for option in name_options:
            menu.add_command(label=option, command=lambda value=option: self.name_selection.set(value))

    def add_appointment(self):
        # Set up the window to add an appointment
        self.add_appointment_window = tk.Toplevel(self)
        self.add_appointment_window.title("Add Appointment")
        self.add_appointment_window.geometry("400x300")

        # Create the frame to organise the display table and buttons
        add_appointment_frame = tk.Frame(self.add_appointment_window)
        add_appointment_frame.pack(padx=10, pady=10)

        # Create the client name label and entry
        appointment_client_name_label = tk.Label(add_appointment_frame, text="*Client Name:")
        appointment_client_name_label.grid(row=0, column=0)
        self.name_selection = tk.StringVar()
        # Open the database and fetch the client names
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT client_id, client_forename, client_surname FROM client")
        clients_names = cursor.fetchall()
        # Close the database connection
        connection.close()
        # Create a list for the different options the user has and display them
        name_options = [""] + [f"{client[0]}, {client[1]} {client[2]}" for client in clients_names]
        self.appointment_name_entry = ttk.OptionMenu(add_appointment_frame, self.name_selection, name_options[0], *name_options)
        self.appointment_name_entry.grid(row=0, column=1)

        # Entry and submit button to search for client names
        self.name_search_entry = tk.Entry(add_appointment_frame)
        self.name_search_entry.grid(row=1, column=1)
        name_search_button = ttk.Button(add_appointment_frame, text="Search", command=lambda: self.search_name(clients_names))
        name_search_button.grid(row=1, column=2)

        # Create the staff name label and entry
        appointment_staff_name_label = tk.Label(add_appointment_frame, text="*Staff Member Assigned:")
        appointment_staff_name_label.grid(row=3, column=0)
        self.staff_name_selection = tk.StringVar()
        # Open the database and fetch the staff names
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("SELECT staff_id, staff_forename, staff_surname FROM staff WHERE staff_status = 'Currently Employed'")
        staff_names = cursor.fetchall()
        # Close the database
        connection.close()
        # Create a list for the different options the user has
        staff_name_options = [""] + [f"{staff[0]}, {staff[1]} {staff[2]}" for staff in staff_names]
        self.appointment_staff_name_entry = ttk.OptionMenu(add_appointment_frame, self.staff_name_selection, staff_name_options[0], *staff_name_options)
        self.appointment_staff_name_entry.grid(row=3, column=1)

        # Widgets for selecting the service
        self.appointment_service_selection = tk.StringVar()
        appointment_service_label = tk.Label(add_appointment_frame, text="*Service:")
        appointment_service_label.grid(row=4, column=0)
        service_options = ["", "legs", "arms", "back"]
        appointment_service_entry = ttk.OptionMenu(add_appointment_frame, self.appointment_service_selection, service_options[0], *service_options)
        appointment_service_entry.grid(row=4, column=1)

        # Widgets for selecting the time
        appointment_time_label = tk.Label(add_appointment_frame, text="*24H Time in HH:MM")
        appointment_time_label.grid(row=5, column=0)
        self.appointment_time_entry = tk.Entry(add_appointment_frame)
        self.appointment_time_entry.grid(row=5, column=1)

        # Widgets for selecting the date
        appointment_date_label = tk.Label(add_appointment_frame, text="*Date as [dd-mm-yyyy]")
        appointment_date_label.grid(row=6, column=0)
        self.appointment_date_entry = DateEntry(add_appointment_frame, date_pattern="dd-mm-yyyy", width=10)
        self.appointment_date_entry.grid(row=6, column=1)

        # Widgets for selecting the status
        self.status_selection = tk.StringVar()
        appointment_status_label = tk.Label(add_appointment_frame, text="*Status:")
        appointment_status_label.grid(row=7, column=0)
        status_options = ["", "Upcoming", "Completed", "Cancelled"]
        self.appointment_status_entry = ttk.OptionMenu(add_appointment_frame, self.status_selection, status_options[0], *status_options)
        self.appointment_status_entry.grid(row=7, column=1)

        # Widgets for entering any additional commments
        appointment_comment_label = tk.Label(add_appointment_frame, text="Comment")
        appointment_comment_label.grid(row=8, column=0)
        self.appointment_comment_entry = tk.Entry(add_appointment_frame)
        self.appointment_comment_entry.grid(row=8, column=1)

        # Button to submit a new appointment
        submit_button = ttk.Button(add_appointment_frame, text="Add New Appointment", command=self.submit_appointment)
        submit_button.grid(row=9, column=0, columnspan=2)
    
    def edit_appointment(self):
        # Retrieve the item that the user has selected
        selected_items = self.appointments_table.selection()
        if not selected_items:
            # If there is an error then display a warning
            messagebox.showwarning("Warning", "Please select an appointment to edit.")
        elif len(selected_items) > 1:
            # If there is an error then display a warning
            messagebox.showwarning("Warning", "Multiple items selected, please only select one to edit.")
        else:
            # Get the appointment ID of the selected appointment
            selected_item = selected_items[0]
            values = self.appointments_table.item(selected_item, 'values')
            appointment_id = values[0]

            try:
                # Connect to the database
                self.connect_database()
                # Retrieve the appointment details for the selected ID
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
                if not row:
                    # If there is an error then display a warning
                    messagebox.showwarning("Warning", "The selected appointment was not found.")
                    return
                else:
                    # Set up the window to edit an appointment
                    self.edit_appointment_window = tk.Toplevel(self)
                    self.edit_appointment_window.title("Edit Appointment")
                    self.edit_appointment_window.geometry("350x300")

                    # Create the frame to organise the display table and buttons
                    edit_appointment_frame = tk.Frame(self.edit_appointment_window)
                    edit_appointment_frame.pack(padx=10, pady=10)

                    # Create the client name label and entry
                    appointment_client_name_label = tk.Label(edit_appointment_frame, text="*Client Name:")
                    appointment_client_name_label.grid(row=0, column=0)
                    self.name_selection = tk.StringVar()
                    connection = sqlite3.connect("database.db")
                    # Open the database and fetch the client names
                    cursor = connection.cursor()
                    cursor.execute("SELECT client_id, client_forename, client_surname FROM client")
                    clients_names = cursor.fetchall()
                    # Close the database connection
                    connection.close()
                    # Create a list for the different options the user has and display them
                    name_options = [row[1]] + [f"{client[0]}, {client[1]} {client[2]}" for client in clients_names]
                    self.appointment_name_entry = ttk.OptionMenu(edit_appointment_frame, self.name_selection, name_options[0], *name_options)
                    self.appointment_name_entry.grid(row=0, column=1)

                    # Entry and submit button to search for client names
                    self.name_search_entry = tk.Entry(edit_appointment_frame)
                    self.name_search_entry.grid(row=1, column=1)
                    name_search_button = ttk.Button(edit_appointment_frame, text="Search", command=lambda: self.search_name(clients_names))
                    name_search_button.grid(row=1, column=2)

                    # Create the staff name label and entry
                    appointment_staff_name_label = tk.Label(edit_appointment_frame, text="*Staff Member Assigned:")
                    appointment_staff_name_label.grid(row=3, column=0)
                    self.staff_name_selection = tk.StringVar()
                    # Open the database and fetch the staff names
                    connection = sqlite3.connect("database.db")
                    cursor = connection.cursor()
                    cursor.execute("SELECT staff_id, staff_forename, staff_surname FROM staff WHERE staff_status = 'Currently Employed'")
                    staff_names = cursor.fetchall()
                    # Close the database connection
                    connection.close()
                    # Create a list for the different options the user has
                    staff_name_options = [row[2]] + [f"{staff[0]}, {staff[1]} {staff[2]}" for staff in staff_names]
                    self.appointment_staff_name_entry = ttk.OptionMenu(edit_appointment_frame, self.staff_name_selection, staff_name_options[0], *staff_name_options)
                    self.appointment_staff_name_entry.grid(row=3, column=1)

                    # Widgets for editing the service
                    self.appointment_service_selection = tk.StringVar()
                    appointment_service_label = tk.Label(edit_appointment_frame, text="*Service:")
                    appointment_service_label.grid(row=4, column=0)
                    service_options = ["", "legs", "arms", "back"]
                    selected_service = row[3]
                    service_selection = tk.StringVar(value=selected_service)
                    appointment_service_entry = ttk.OptionMenu(edit_appointment_frame, self.appointment_service_selection, selected_service, *service_options)
                    appointment_service_entry.grid(row=4, column=1)

                    # Widgets for editing the time
                    appointment_time_label = tk.Label(edit_appointment_frame, text="*24H Time in HH:MM")
                    appointment_time_label.grid(row=5, column=0)
                    self.appointment_time_entry = tk.Entry(edit_appointment_frame)
                    self.appointment_time_entry.grid(row=5, column=1)
                    self.appointment_time_entry.insert(0, row[4])

                    # Widgets for editing the date
                    appointment_date_label = tk.Label(edit_appointment_frame, text="*Date as [dd-mm-yyyy]")
                    appointment_date_label.grid(row=6, column=0)
                    self.appointment_date_entry_var = tk.StringVar(value=row[5])
                    self.appointment_date_entry = DateEntry(edit_appointment_frame, date_pattern="dd-mm-yyyy", width=10, textvariable=self.appointment_date_entry_var)
                    self.appointment_date_entry.grid(row=6, column=1)
                    self.appointment_date_entry_var.set(row[5])

                    # Widgets for editing the status
                    self.status_selection = tk.StringVar()
                    appointment_status_label = tk.Label(edit_appointment_frame, text="*Status:")
                    appointment_status_label.grid(row=7, column=0)
                    status_options = ["", "Upcoming", "Completed", "Cancelled"]
                    selected_status = row[6]
                    status_selection = tk.StringVar(value=selected_status)
                    self.appointment_status_entry = ttk.OptionMenu(edit_appointment_frame, self.status_selection, selected_status, *status_options)
                    self.appointment_status_entry.grid(row=7, column=1)

                    # Widgets for editing the comments
                    appointment_comment_label = tk.Label(edit_appointment_frame, text="Comment")
                    appointment_comment_label.grid(row=8, column=0)
                    self.appointment_comment_entry = tk.Entry(edit_appointment_frame)
                    self.appointment_comment_entry.grid(row=8, column=1)
                    self.appointment_comment_entry.insert(0, row[7])

                    # Button to update the selected appointment
                    submit_button = ttk.Button(edit_appointment_frame, text="Update Appointment", command=self.submit_appointment)
                    submit_button.grid(row=9, column=0, columnspan=2)                
                    
            except sqlite3.Error as e:
                # If there is an SQL error then display a warning
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                # Close the database connection
                self.cursor.close()
                self.conn.close()

    def submit_appointment(self):
        # Retrieve the values from the entry boxes
        client_name = self.name_selection.get()
        staff_name = self.staff_name_selection.get()
        service_name = self.appointment_service_selection.get()
        time = self.appointment_time_entry.get()
        date = self.appointment_date_entry.get()
        status = self.status_selection.get()
        comment = self.appointment_comment_entry.get()

        # Check to make sure that the required fields aren't empty
        if not client_name or not staff_name or not service_name or not time or not date or not status:
            # If there is an error then display a warning
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        # Connect to the database
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        try:
            # Extract the selected client ID and staff ID
            client_id = int(client_name.split(",")[0])
            staff_id = int(staff_name.split(",")[0])

            # Insert the appointment data into the database
            cursor.execute('''
                INSERT INTO appointment (client_id, staff_id, service_id, appointment_session_time, appointment_session_date, appointment_status, appointment_comments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (client_id, staff_id, service_name, time, date, status, comment))

            # Commit the changes to the database and then close
            connection.commit()
            connection.close()
            # Display a message to the user
            messagebox.showinfo("Info", "Appointment added successfully!")
            # Close the "add appointment" window and refresh the display table
            self.add_appointment_window.destroy()
            self.fetch_and_display()

        except sqlite3.Error as e:
            # If there is an error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Make sure that the database is closed even if there is an exception
            if connection:
                connection.close()

    def delete_appointment(self):
        # Get the selected items from the appointments table
        selected_items = self.appointments_table.selection()

        if not selected_items:
            # If there is an error then display a warning
            messagebox.showwarning("Warning", "Please select appointment(s) to delete.")
            return

        # Get the number of selected appointments
        number_selected = len(selected_items)
        # Get user to confirm the deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} appointment(s)?")
        if not confirm:
            return

        # Connect to the database
        self.connect_database()

        try:
            # Loop through the selected items and delete the associated item from the appointments database
            for item in selected_items:
                appointment_id = self.appointments_table.item(item, 'values')[0]
                self.cursor.execute("DELETE FROM appointment WHERE appointment_id=?", (appointment_id,))
                self.appointments_table.delete(item)

            # Commit the changes to the database
            self.conn.commit()
            # If done correctly then show a sucess message to the user
            messagebox.showinfo("Info", "Appointment(s) deleted successfully!")
        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def select_all(self):
        # Get all the items in the appointments display table and show them as selected to the user
        items = self.appointments_table.get_children()
        for item in items:
            self.appointments_table.selection_add(item)

    def export_selected(self):
        # Get the selected items from the appointments table
        selected_items = self.appointments_table.selection()

        # Check if there are any appointments selected
        if not selected_items:
            # If no appointment is selected then display a warning
            messagebox.showwarning("Warning", "No appointments selected for export.")
            return

        # Connect to the database
        self.connect_database()

        try:
            appointment_data = []
            # Retrieve the data for the selected appointments from the database
            for item in selected_items:
                # Extract the appointment ID from the item ID
                appointment_id = self.appointments_table.item(item, 'values')[0]
                row = self.cursor.execute("SELECT * FROM appointment WHERE appointment_id=?", (appointment_id,)).fetchone()
                if row:
                    appointment_data.append(row)

            if appointment_data:
                # If there is selected appointments then export as a Microsoft Excel file (.xlsx)
                columns = ["appointment_id", "client_id", "staff_id", "service_id", "appointment_session_time", "appointment_session_date", "appointment_status", "appointment_comments"]
                df = pd.DataFrame(appointment_data, columns=columns)

                # Allow the user to chose where to save the file by opening File Explorer
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    # Save the data as a Microsoft Excel file
                    df.to_excel(file_path, index=False)
                    # If successful then display a message to the user
                    messagebox.showinfo("Info", "Selected appointment(s) exported to Excel successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

# This class allows the user to create and interact with all stored clients
class clients_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        # Set up the clients window
        self.title("Clients")
        self.geometry("550x600")

        # Create a heading frame to display the logo
        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)
        # Display the logo
        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        # Create the clients display table
        self.client_table = ttk.Treeview(self, columns=('ID', 'Name', 'DOB', 'Gender', 'Email', 'Phone'), show='headings', height=14)

        # Create columns to the display table
        self.client_table.column('ID', width=30)
        self.client_table.column('Name', width=120)
        self.client_table.column('DOB', width=70)
        self.client_table.column('Gender', width=50)
        self.client_table.column('Email', width=150)
        self.client_table.column('Phone', width=75)

        # Give each column a heading in the display table
        self.client_table.heading('ID', text='ID')
        self.client_table.heading('Name', text='Name')
        self.client_table.heading('DOB', text='DOB')
        self.client_table.heading('Gender', text='Gender')
        self.client_table.heading('Email', text='Email')
        self.client_table.heading('Phone', text='Phone')
        self.client_table.pack(pady=20)

        # Fetch and display the clients from the database
        self.fetch_and_display()

        # Create the menu frame to display the buttons
        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        # Create and display the buttons
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

    def connect_database(self):
        # Establish a connection to the database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
        # Fetch the clients from the database and then display them in the table
        #  Connect to the database
        self.connect_database()
        # This query takes the client IDs stored in the clients table and searches the database
        query = '''
        SELECT client_id, client_forename || ' ' || client_surname AS Name, client_DOB AS DOB, client_gender AS Gender, client_email AS Email, client_phone as Phone
        FROM client
        ORDER BY Name
        '''
        # Insert the rows from the database into the clients display table
        rows = self.cursor.execute(query).fetchall()
        for row in rows:
            self.client_table.insert("", "end", iid=row[0], values=row) 

    def view_client(self):
        # Retrieve the client that the user has selected
        selected_item = self.client_table.selection()
        if not selected_item:
            # If no client has been selected then display a warning
            messagebox.showwarning("Warning", "Please select a client to view.")
            return

        # Gets the client ID from the selected row
        client_id = selected_item[0]
        # Connect to the database
        self.connect_database()

        try:
            # Retrieve the associated client details from the database for the selected client ID
            row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
            # Check if a row has been retrieved
            if not row:
                # If no row has been selected then display a warning
                messagebox.showwarning("Warning", "The selected client was not found.")
                return

            # Set up a new window to view the client details
            self.view_client_window = tk.Toplevel(self)
            self.view_client_window.title("View Client")
            self.view_client_window.geometry("300x300")

            # Create a frame to display the clients details
            view_client_frame = tk.Frame(self.view_client_window)
            view_client_frame.pack(padx=10, pady=10)

            # Create and display the labels and data from the selected client ID
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
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def add_client(self):
        # Set up the window to add a client
        self.add_client_window = tk.Toplevel(self)
        self.add_client_window.title("Add Client")
        self.add_client_window.geometry("300x300")

        # Create the frame to organise the display table and buttons
        add_client_frame = tk.Frame(self.add_client_window)
        add_client_frame.pack(padx=10, pady=10)

        # Create the label and entry boxes for the user to input data
        # Widgets for client forename entry
        client_forename_label = tk.Label(add_client_frame, text="*Forename:")
        client_forename_label.grid(row=0, column=0)
        self.client_forename_entry = tk.Entry(add_client_frame)
        self.client_forename_entry.grid(row=0, column=1)
        
        # Widgets for client surname entry
        client_surname_label = tk.Label(add_client_frame, text="*Surname:")
        client_surname_label.grid(row=1, column=0)
        self.client_surname_entry = tk.Entry(add_client_frame)
        self.client_surname_entry.grid(row=1, column=1)
        
        # Widgets for client DOB entry
        client_dob_label = tk.Label(add_client_frame, text="*DOB:")
        client_dob_label.grid(row=2, column=0)
        self.client_dob_entry = tk.Entry(add_client_frame)
        self.client_dob_entry.grid(row=2, column=1)

        # Widgets for client gender entry
        self.gender_selection = tk.StringVar()
        client_gender_label = tk.Label(add_client_frame, text="*Gender:")
        client_gender_label.grid(row=3, column=0)
        gender_options = ["", "Male", "Female", "Other"]
        gender_entry = ttk.OptionMenu(add_client_frame, self.gender_selection, gender_options[0], *gender_options)
        gender_entry.grid(row=3, column=1)

        # Widgets for client phone entry
        client_phone_label = tk.Label(add_client_frame, text="(*)Phone:")
        client_phone_label.grid(row=4, column=0)
        self.client_phone_entry = tk.Entry(add_client_frame)
        self.client_phone_entry.grid(row=4, column=1)
        
        # Widgets for client email entry
        client_email_label = tk.Label(add_client_frame, text="(*)Email:")
        client_email_label.grid(row=5, column=0)
        self.client_email_entry = tk.Entry(add_client_frame)
        self.client_email_entry.grid(row=5, column=1)

        # Widgets for client address entry
        client_address_label = tk.Label(add_client_frame, text="Address:")
        client_address_label.grid(row=6, column=0)
        self.client_address_entry = tk.Entry(add_client_frame)
        self.client_address_entry.grid(row=6, column=1)

        # Widgets for client comments entry
        client_comments_label = tk.Label(add_client_frame, text="Comments:")
        client_comments_label.grid(row=8, column=0)
        self.client_comments_entry = tk.Entry(add_client_frame)
        self.client_comments_entry.grid(row=8, column=1)

        # Button to create a new appointment
        submit_button = ttk.Button(add_client_frame, text="Add New Client", command=self.submit_client)
        submit_button.grid(row=9, column=0, columnspan=2)

    def submit_client(self):
        # Retrieve the values from the entry boxes
        forename = self.client_forename_entry.get()
        surname = self.client_surname_entry.get()
        DOB = self.client_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        address = self.client_address_entry.get()
        comments = self.client_comments_entry.get()

        # Check to make sure that the required fields aren't empty
        if not forename or not surname or not DOB or not gender:
            # If all the inputs aren't present then display a warning
            messagebox.showerror("Error", "Fields marked with * are required!")
            return
        
        # Check to make sure that either a phone or email is present
        if not (phone or email):
            # If there is no phone number and email address then display a warning
            messagebox.showerror("Error", "Either a phone number or an email address is required!")
            return

        # Check to make sure that the dates are in the correct day-month-year format
        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            # If there is an error then display a warning
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        # Check to make sure that the phone number is digits only
        if phone and not phone.isdigit():
            # If there is an error then display a warning
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        # Check to make sure that the email is in the correct format
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # If the email is in the incorrect format display a warning
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            # Connnect to the database
            self.connect_database()
            # Add a new client into the table
            self.cursor.execute("INSERT INTO client (client_forename, client_surname, client_DOB, client_gender, client_phone, client_email, client_address, client_comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (forename, surname, DOB, gender, phone, email, address, comments))
            # Commit the changes to the database
            self.conn.commit()

            # Clear all the rows and then fetch and display the information to the display table
            for row in self.client_table.get_children():
                self.client_table.delete(row)
            self.fetch_and_display()

            # Close the add client window
            self.add_client_window.destroy()

            # Display a success message to the user
            messagebox.showinfo("Info", "Client added successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def edit_client(self):
        # Retrieve the client that the user has selected
        selected_items = self.client_table.selection()
        if not selected_items:
            # If nothing was selected then display a warning
            messagebox.showwarning("Warning", "Please select a client to edit.")
        elif len(selected_items) > 1:
            # If there there are more than one things selected then display a warning
            messagebox.showwarning("Warning", "Multiple items selected, please only select one to edit.")
        else:
            # Get the client ID of the selected client
            client_id = selected_items[0]
            # Connect to the database
            self.connect_database()

            try:
                # Get everything from the database from the selected client
                row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
                if not row:
                    # If there isnt a row then display a warning
                    messagebox.showwarning("Warning", "The selected client was not found.")
                else:
                    # Set up the window to edit a client
                    self.edit_client_window = tk.Toplevel(self)
                    self.edit_client_window.title("Edit Client")
                    self.edit_client_window.geometry("300x300")

                    # Create the frame to organise the display table and the buttons
                    edit_client_frame = tk.Frame(self.edit_client_window)
                    edit_client_frame.pack(padx=10, pady=10)

                    # Create the client forename label and entry and insert the associated infomation
                    client_forename_label = tk.Label(edit_client_frame, text="*Forename:")
                    client_forename_label.grid(row=0, column=0)
                    self.client_forename_entry = tk.Entry(edit_client_frame)
                    self.client_forename_entry.grid(row=0, column=1)
                    self.client_forename_entry.insert(0, row[1])

                    # Create the client surname label and entry and insert the associated infomation
                    client_surname_label = tk.Label(edit_client_frame, text="*Surname:")
                    client_surname_label.grid(row=1, column=0)
                    self.client_surname_entry = tk.Entry(edit_client_frame)
                    self.client_surname_entry.grid(row=1, column=1)
                    self.client_surname_entry.insert(0, row[2])

                    # Create the client surname label and entry and insert the associated infomation
                    client_dob_label = tk.Label(edit_client_frame, text="*DOB:")
                    client_dob_label.grid(row=2, column=0)
                    self.client_dob_entry = tk.Entry(edit_client_frame)
                    self.client_dob_entry.grid(row=2, column=1)
                    self.client_dob_entry.insert(0, row[3])

                    # Create the client surname label and entry and insert the associated infomation
                    self.gender_selection = tk.StringVar()
                    client_gender_label = tk.Label(edit_client_frame, text="*Gender:")
                    client_gender_label.grid(row=3, column=0)
                    gender_options = ["", "Male", "Female", "Other"]
                    selected_gender = row[4]
                    gender_selection = tk.StringVar(value=selected_gender)
                    client_gender_entry = ttk.OptionMenu(edit_client_frame, self.gender_selection, selected_gender, *gender_options)
                    client_gender_entry.grid(row=3, column=1)

                    # Create the client surname label and entry and insert the associated infomation
                    client_phone_label = tk.Label(edit_client_frame, text="Phone:")
                    client_phone_label.grid(row=4, column=0)
                    self.client_phone_entry = tk.Entry(edit_client_frame)
                    self.client_phone_entry.grid(row=4, column=1)
                    self.client_phone_entry.insert(0, row[5])

                    # Create the client surname label and entry and insert the associated infomation
                    client_email_label = tk.Label(edit_client_frame, text="Email:")
                    client_email_label.grid(row=5, column=0)
                    self.client_email_entry = tk.Entry(edit_client_frame)
                    self.client_email_entry.grid(row=5, column=1)
                    self.client_email_entry.insert(0, row[6])

                    # Create the client surname label and entry and insert the associated infomation
                    client_address_label = tk.Label(edit_client_frame, text="Address:")
                    client_address_label.grid(row=6, column=0)
                    self.client_address_entry = tk.Entry(edit_client_frame)
                    self.client_address_entry.grid(row=6, column=1)
                    self.client_address_entry.insert(0, row[7])

                    # Create the client comments and entry and insert the associated infomation
                    client_comments_label = tk.Label(edit_client_frame, text="Comments:")
                    client_comments_label.grid(row=8, column=0)
                    self.client_comments_entry = tk.Entry(edit_client_frame)
                    self.client_comments_entry.grid(row=8, column=1)
                    self.client_comments_entry.insert(0, row[8])

                    # Button to update the selected client
                    submit_button = ttk.Button(edit_client_frame, text="Update Client", command=lambda: self.update_client(row[0]))
                    submit_button.grid(row=9, column=0, columnspan=2)

            except sqlite3.Error as e:
                # If there is an SQL error then display a warning
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                # Close the database connection
                self.conn.close()

    def update_client(self, client_id):
        # Retrieve the values from the entry boxes
        forename = self.client_forename_entry.get()
        surname = self.client_surname_entry.get()
        DOB = self.client_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.client_phone_entry.get()
        email = self.client_email_entry.get()
        address = self.client_address_entry.get()
        comments = self.client_comments_entry.get()

        # Check to make sure that the required fields aren't empty
        if not forename or not surname or not DOB or not gender:
            # If there is an error then display a warning
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        # Check to make sure that the date is in the valid day-month-year format
        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            # If certain data is missing then display a warning
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        # Check to make sure that the phone number is digits only
        if phone and not phone.isdigit():
            # If the phone number isn't just digits then display a warning
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        # Check to make sure that the email is in the correct format
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # If the email isn't in the correct format then display a warning# If there is an error then display a warning
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            # Connect to the database
            self.connect_database()
            # Update the client information
            self.cursor.execute("""
                UPDATE client 
                SET client_forename=?, client_surname=?, client_DOB=?, client_gender=?, client_phone=?, client_email=?, client_address=?, client_comments=? 
                WHERE client_id=?
            """, (forename, surname, DOB, gender, phone, email, address, comments, client_id))
            # Commit the changes to the database
            self.conn.commit()

            # Clear the existing rows in the client display table
            # Then fetch and display the table with the database information
            for row in self.client_table.get_children():
                self.client_table.delete(row)
            self.fetch_and_display()

            # Close the edit client window
            self.edit_client_window.destroy()
            # Display a success message to the user
            messagebox.showinfo("Info", "Client updated successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def delete_client(self):
        # Get the selected items from the clients display table
        selected_items = self.client_table.selection()

        if not selected_items:
            # If no items are selected then display a warning
            messagebox.showwarning("Warning", "Please select a client to delete.")
            return

        # Get the number of selected clients
        number_selected = len(selected_items)
        # Get the user to confirm the deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} client(s)?")
        if not confirm:
            return

        # Connect to the database
        self.connect_database()

        try:
            # Loop through the selected items and delete the associated item from the clients database
            for client_id in selected_items:
                self.cursor.execute("DELETE FROM client WHERE client_id=?", (client_id,))
                self.client_table.delete(client_id)

            # Commit the changes to the database
            self.conn.commit()
            # If done correctly then show a success message to the user
            messagebox.showinfo("Info", "Clients deleted successfully!")
        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def select_all(self):
        # Get all the items in the clients table
        items = self.client_table.get_children()
        for item in items:
            self.client_table.selection_add(item)

    def export_selected(self):
        # Get all the selected items from the clients table
        selected_items = self.client_table.selection()
        
        # Check if there are any clients selected
        if not selected_items:
            # If no client is selected then display a warning
            messagebox.showwarning("Warning", "No clients selected for export.")
            return
        
        # Connect to the database
        self.connect_database()

        try:
            client_data = []
            # Retrieve the data for the selected clients from the database
            for client_id in selected_items:
                # Extract the client ID from the item ID
                row = self.cursor.execute("SELECT * FROM client WHERE client_id=?", (client_id,)).fetchone()
                if row:
                    client_data.append(row)

            if client_data:
                # If there are selected clients then export them as a Microsoft Excel file (.xlsx)
                df = pd.DataFrame(client_data, columns=["client_id", "client_forename", "client_surname", "client_DOB", "client_gender", "client_phone", "client_email", "client_address", "client_comments"])

                # Allow the user to chose where to save the file by opening File Explorer
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    # Save the data as a Microsoft Excel file
                    df.to_excel(file_path, index=False)
                    # If successful then display a message to the user
                    messagebox.showinfo("Info", "Selected clients exported to Excel successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

# This class allows the user to create and interact with all stored staff members
class staff_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        # Set up the staff window
        self.title("Staff")
        self.geometry("500x600")

        # Create a heading frame to display the logo
        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10)
        # Display the logo
        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(12, 12)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=0, padx=10, pady=5)

        # Create the staff display table
        self.staff_table = ttk.Treeview(self, columns=('Name', 'Gender', 'DOB', 'Status'), show='headings', height=14)

        # Create the columns for the display table
        self.staff_table.column('Name', width=170)
        self.staff_table.column('Gender', width=50)
        self.staff_table.column('DOB', width=70)
        self.staff_table.column('Status', width=120)

        # Give each column a heading in the display table
        self.staff_table.heading('Name', text='Name')
        self.staff_table.heading('Gender', text='Gender')
        self.staff_table.heading('DOB', text='DOB')
        self.staff_table.heading('Status', text='Status')
        self.staff_table.pack(pady=20)

        # Fetch and display the staff from the database
        self.fetch_and_display()

        # Create the menu frame to display the buttons
        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        # Create and display the buttons
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

    def connect_database(self):
        # Establish a connection to the database
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def fetch_and_display(self):
        # Fetch the staff from the database and then display them in the table
        # Connect to the database
        self.connect_database()
        # This query takes the staff IDs stored in the staff table and searches the database
        query = '''
        SELECT staff_id, staff_forename || ' ' || staff_surname AS Name, staff_gender AS Gender, staff_DOB AS DOB, staff_status AS Status
        FROM staff
        ORDER BY Name
        '''
        # Insert the rows from the database into the staff display table
        rows = self.cursor.execute(query).fetchall()
        for row in rows:
            self.staff_table.insert("", "end", iid=row[0], values=row[1:])  

    def view_staff_member(self):
        # Retrieve the staff member that the user has selected
        selected_item = self.staff_table.selection()
        if not selected_item:
            # If no staff member has been selected then display a warning
            messagebox.showwarning("Warning", "Please select a staff member to view.")
            return

        # Get the staff ID from the selected row
        staff_id = selected_item[0]
        # Connect to the database
        self.connect_database()

        try:
            # Retrieve the associated staff details from the database for the selected staff ID
            row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
            # Check if a row has been retrieved
            if not row:
                # If no row has been selected then display a warning to the user
                messagebox.showwarning("Warning", "The selected staff member was not found.")
                return

            # Set up a new window to view the staff details
            self.view_staff_window = tk.Toplevel(self)
            self.view_staff_window.title("View Staff Member")
            self.view_staff_window.geometry("300x300")

            # Create a frame to display the staff details
            view_staff_frame = tk.Frame(self.view_staff_window)
            view_staff_frame.pack(padx=10, pady=10)

            # Create and display the labels and data from the selected staff ID
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
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def add_staff_member(self):
        # Set up the window to add a staff member
        self.add_staff_window = tk.Toplevel(self)
        self.add_staff_window.title("Add Staff Member")
        self.add_staff_window.geometry("300x300")

        # Create the frame to organise the display table and buttons
        add_staff_frame = tk.Frame(self.add_staff_window)
        add_staff_frame.pack(padx=10, pady=10)

        # Create the label and entry boxes for the user to input data
        # Widgets for staff forename entry
        staff_forename_label = tk.Label(add_staff_frame, text="*Forename:")
        staff_forename_label.grid(row=0, column=0)
        self.staff_forename_entry = tk.Entry(add_staff_frame)
        self.staff_forename_entry.grid(row=0, column=1)
        
        # Widgets for staff surname entry
        staff_surname_label = tk.Label(add_staff_frame, text="*Surname:")
        staff_surname_label.grid(row=1, column=0)
        self.staff_surname_entry = tk.Entry(add_staff_frame)
        self.staff_surname_entry.grid(row=1, column=1)
        
        # Widgets for staff DOB entry
        staff_dob_label = tk.Label(add_staff_frame, text="*DOB:")
        staff_dob_label.grid(row=2, column=0)
        self.staff_dob_entry = tk.Entry(add_staff_frame)
        self.staff_dob_entry.grid(row=2, column=1)

        # Widgets for staff gender entry
        self.gender_selection = tk.StringVar()
        staff_gender_label = tk.Label(add_staff_frame, text="*Gender:")
        staff_gender_label.grid(row=3, column=0)
        gender_options = ["", "Male", "Female", "Other"]
        gender_entry = ttk.OptionMenu(add_staff_frame, self.gender_selection, gender_options[0], *gender_options)
        gender_entry.grid(row=3, column=1)

        # Widgets for staff phone entry
        staff_phone_label = tk.Label(add_staff_frame, text="Phone:")
        staff_phone_label.grid(row=4, column=0)
        self.staff_phone_entry = tk.Entry(add_staff_frame)
        self.staff_phone_entry.grid(row=4, column=1)
        
        # Widgets for staff email entry
        staff_email_label = tk.Label(add_staff_frame, text="Email:")
        staff_email_label.grid(row=5, column=0)
        self.staff_email_entry = tk.Entry(add_staff_frame)
        self.staff_email_entry.grid(row=5, column=1)

        # Widgets for staff address entry
        staff_address_label = tk.Label(add_staff_frame, text="Address:")
        staff_address_label.grid(row=6, column=0)
        self.staff_address_entry = tk.Entry(add_staff_frame)
        self.staff_address_entry.grid(row=6, column=1)

        # Widgets for staff status entry
        self.status_selection = tk.StringVar()
        staff_status_label = tk.Label(add_staff_frame, text="*Status:")
        staff_status_label.grid(row=7, column=0)
        status_options = ["Currently Employed", "Previously Employed", "Not Employed", "Other"]
        self.status_entry = ttk.OptionMenu(add_staff_frame, self.status_selection, status_options[0], *status_options)
        self.status_entry.grid(row=7, column=1)

        # Widgets for staff comments entry
        staff_comments_label = tk.Label(add_staff_frame, text="Comments:")
        staff_comments_label.grid(row=8, column=0)
        self.staff_comments_entry = tk.Entry(add_staff_frame)
        self.staff_comments_entry.grid(row=8, column=1)

        # Button to create a new staff member
        submit_button = ttk.Button(add_staff_frame, text="Add New Staff Member", command=self.submit_staff)
        submit_button.grid(row=9, column=0, columnspan=2)

    def submit_staff(self):
        # Retrieve the values from the entry boxes
        forename = self.staff_forename_entry.get()
        surname = self.staff_surname_entry.get()
        DOB = self.staff_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.staff_phone_entry.get()
        email = self.staff_email_entry.get()
        address = self.staff_address_entry.get()
        status = self.status_selection.get()
        comments = self.staff_comments_entry.get()

        # Check to make sure that the required fields aren't empty
        if not forename or not surname or not DOB or not gender or not status:
            # If all the inputs aren't present then display a warning
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        # Check to make sure that the data is in the valid day-month-year format
        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            # If there is an error then display a warning
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        # Check to make sure that the phone number is digits only
        if phone and not phone.isdigit():
            # If there is an error then display a warning
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        # Check to make sure that the email is in the correct format
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # If there is an error then display a warning
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            # Connect to the database
            self.connect_database()
            # Add a new staff member's information into the database
            self.cursor.execute("INSERT INTO staff (staff_forename, staff_surname, staff_DOB, staff_gender, staff_phone, staff_email, staff_address, staff_status, staff_comments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (forename, surname, DOB, gender, phone, email, address, status, comments))
            # Commit the changes to the database
            self.conn.commit()

            # Clear all the rows and then fetch and display the information to the display table
            for row in self.staff_table.get_children():
                self.staff_table.delete(row)
            self.fetch_and_display()

            # Close the add staff window
            self.add_staff_window.destroy()

            # Display a success messsage to the user
            messagebox.showinfo("Info", "Staff member added successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # CLose the database connection
            self.conn.close()

    def edit_staff_member(self):
        # Retrieve the staff member that the user has selected
        selected_items = self.staff_table.selection()
        if not selected_items:
            # If nothing was selected then display a warning
            messagebox.showwarning("Warning", "Please select a staff member to edit.")
        elif len(selected_items) > 1:
            # If there there are more than one things selected then display a warning
            messagebox.showwarning("Warning", "Multiple items selected, please only select one to edit.")
        else:
            # Get the staff ID of the selected staff member
            staff_id = selected_items[0]
            # Connect to the database
            self.connect_database()

            try:
                # Get everything from the database from the selected staff member
                row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
                if not row:
                    # If there isnt a row then display a warning
                    messagebox.showwarning("Warning", "The selected staff member was not found.")
                else:
                    # Set up the window to edit a staff member
                    self.edit_staff_window = tk.Toplevel(self)
                    self.edit_staff_window.title("Edit Staff Member")
                    self.edit_staff_window.geometry("300x300")

                    # Create a frame to organise the display table and the buttons
                    edit_staff_frame = tk.Frame(self.edit_staff_window)
                    edit_staff_frame.pack(padx=10, pady=10)

                    # Create the staff forename label and entry and insert the associated infomation 
                    staff_forename_label = tk.Label(edit_staff_frame, text="*Forename:")
                    staff_forename_label.grid(row=0, column=0)
                    self.staff_forename_entry = tk.Entry(edit_staff_frame)
                    self.staff_forename_entry.grid(row=0, column=1)
                    self.staff_forename_entry.insert(0, row[1])

                    # Create the staff surname label and entry and insert the associated infomation
                    staff_surname_label = tk.Label(edit_staff_frame, text="*Surname:")
                    staff_surname_label.grid(row=1, column=0)
                    self.staff_surname_entry = tk.Entry(edit_staff_frame)
                    self.staff_surname_entry.grid(row=1, column=1)
                    self.staff_surname_entry.insert(0, row[2])

                    # Create the staff DOB label and entry and insert the associated infomation
                    staff_dob_label = tk.Label(edit_staff_frame, text="*DOB:")
                    staff_dob_label.grid(row=2, column=0)
                    self.staff_dob_entry = tk.Entry(edit_staff_frame)
                    self.staff_dob_entry.grid(row=2, column=1)
                    self.staff_dob_entry.insert(0, row[3])

                    # Create the staff gender label and entry and insert the associated infomation
                    self.gender_selection = tk.StringVar()
                    staff_gender_label = tk.Label(edit_staff_frame, text="*Gender:")
                    staff_gender_label.grid(row=3, column=0)
                    gender_options = ["", "Male", "Female", "Other"]
                    selected_gender = row[4]
                    gender_selection = tk.StringVar(value=selected_gender)
                    staff_gender_entry = ttk.OptionMenu(edit_staff_frame, self.gender_selection, selected_gender, *gender_options)
                    staff_gender_entry.grid(row=3, column=1)

                    # Create the staff phone number label and entry and insert the associated infomation
                    staff_phone_label = tk.Label(edit_staff_frame, text="Phone:")
                    staff_phone_label.grid(row=4, column=0)
                    self.staff_phone_entry = tk.Entry(edit_staff_frame)
                    self.staff_phone_entry.grid(row=4, column=1)
                    self.staff_phone_entry.insert(0, row[5])

                    # Create the staff email address label and entry and insert the associated infomation
                    staff_email_label = tk.Label(edit_staff_frame, text="Email:")
                    staff_email_label.grid(row=5, column=0)
                    self.staff_email_entry = tk.Entry(edit_staff_frame)
                    self.staff_email_entry.grid(row=5, column=1)
                    self.staff_email_entry.insert(0, row[6])

                    # Create the staff address label and entry and insert the associated infomation
                    staff_address_label = tk.Label(edit_staff_frame, text="Address:")
                    staff_address_label.grid(row=6, column=0)
                    self.staff_address_entry = tk.Entry(edit_staff_frame)
                    self.staff_address_entry.grid(row=6, column=1)
                    self.staff_address_entry.insert(0, row[7])

                    # Create the staff status label and entry and insert the associated infomation
                    self.status_selection = tk.StringVar()
                    staff_status_label = tk.Label(edit_staff_frame, text="*Status:")
                    staff_status_label.grid(row=7, column=0)
                    status_options = ["Currently Employed", "Previously Employed", "Not Employed", "Other"]
                    selected_status = row[8]
                    status_selection = tk.StringVar(value=selected_status)
                    staff_status_entry = ttk.OptionMenu(edit_staff_frame, self.status_selection, selected_status, *status_options)
                    staff_status_entry.grid(row=7, column=1)

                    # Create the staff comments label and entry and insert the associated infomation
                    staff_comments_label = tk.Label(edit_staff_frame, text="Comments:")
                    staff_comments_label.grid(row=8, column=0)
                    self.staff_comments_entry = tk.Entry(edit_staff_frame)
                    self.staff_comments_entry.grid(row=8, column=1)
                    self.staff_comments_entry.insert(0, row[9])

                    # Button to update the selected client
                    submit_button = ttk.Button(edit_staff_frame, text="Update Staff Member", command=lambda: self.update_staff(row[0]))
                    submit_button.grid(row=9, column=0, columnspan=2)

            except sqlite3.Error as e:
                # If there is an SQL error then display a warning
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                # Close the databaes connection
                self.conn.close()

    def update_staff(self, staff_id):
        # Retrieve the values from the entry boxes
        forename = self.staff_forename_entry.get()
        surname = self.staff_surname_entry.get()
        DOB = self.staff_dob_entry.get()
        gender = self.gender_selection.get()
        phone = self.staff_phone_entry.get()
        email = self.staff_email_entry.get()
        address = self.staff_address_entry.get()
        status = self.status_selection.get()
        comments = self.staff_comments_entry.get()

        # Check to make sure that the required fields aren't empty
        if not forename or not surname or not DOB or not gender or not status:
            # If certain data is missing then display a warning
            messagebox.showerror("Error", "Fields marked with * are required!")
            return

        # Check to make sure that the date is in the valid day-month-year format
        if not re.match(r'\d{2}/\d{2}/\d{4}', DOB):
            messagebox.showerror("Error", "Invalid DOB format. Use dd/mm/yyyy")
            return

        # Check to make sure that the phone number is digits only
        if phone and not phone.isdigit():
            # If the phone number isn't just digits then display a warning
            messagebox.showerror("Error", "Phone number should only contain digits.")
            return

        # Check to make sure that the email is in the correct format
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # If the email isn't in the correct format then display a warning
            messagebox.showerror("Error", "Invalid email format.")
            return

        try:
            # Connect to the database
            self.connect_database()
            # Update the staff information
            self.cursor.execute("""
                UPDATE staff 
                SET staff_forename=?, staff_surname=?, staff_DOB=?, staff_gender=?, staff_phone=?, staff_email=?, staff_address=?, staff_status=?, staff_comments=? 
                WHERE staff_id=?
            """, (forename, surname, DOB, gender, phone, email, address, status, comments, staff_id))
            # Commit the changes to the database
            self.conn.commit()

            # Clear the existing rows in the staff display table
            # Then fetch and display the table with the database information
            for row in self.staff_table.get_children():
                self.staff_table.delete(row)
            self.fetch_and_display()

            # Close the edit staff window
            self.edit_staff_window.destroy()
            # Display a success message to the user
            messagebox.showinfo("Info", "Staff member updated successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def delete_staff_member(self):
        # Get the selected staff member from the staff display table
        selected_items = self.staff_table.selection()

        if not selected_items:
            # If no items are selected then display a warning
            messagebox.showwarning("Warning", "Please select staff members to delete.")
            return

        # Get the number of selected staff members
        number_selected = len(selected_items)
        # Get the user to confirm the deletion
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {number_selected} staff member(s)?")
        if not confirm:
            return

        # Connect to the database
        self.connect_database()
        try:
            # Loop through all the selected staff members and delete the associated item from the staff database table
            for staff_id in selected_items:
                self.cursor.execute("DELETE FROM staff WHERE staff_id=?", (staff_id,))
                self.staff_table.delete(staff_id)

            # Commit the changes to the database
            self.conn.commit()
            # If done correctly then show a success message to the user
            messagebox.showinfo("Info", "Staff members deleted successfully!")
        except sqlite3.Error as e:
            # If there is an SQL error then display a warning to the user
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

    def select_all(self):
        # Get all the items in the staff table
        items = self.staff_table.get_children()
        for item in items:
            self.staff_table.selection_add(item)

    def export_selected(self):
        # Get all the selected items from the staff table
        selected_items = self.staff_table.selection()

        # Check if there are any staff members selected
        if not selected_items:
            # If no staff member is selected then display a warning to the user
            messagebox.showwarning("Warning", "No staff members selected for export.")
            return
        
        # Connect to the database
        self.connect_database()

        try:
            staff_data = []
            # Retrieve the data for the selected staff members from the database
            for staff_id in selected_items:
                # Extract the staff ID from the selected staff members ID
                row = self.cursor.execute("SELECT * FROM staff WHERE staff_id=?", (staff_id,)).fetchone()
                if row:
                    staff_data.append(row)

            if staff_data:
                # If there are selected staff members then export them as a Microsoft Excel (.xlsx)
                df = pd.DataFrame(staff_data, columns=["staff_id", "staff_forename", "staff_surname", "staff_DOB", "staff_gender", "staff_phone", "staff_email", "staff_address", "staff_status", "staff_comments"])

                # Allow the user to chose where to save the file by opening File Explorer
                file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

                if file_path:
                    # Save the data as a Microsoft Excel file
                    df.to_excel(file_path, index=False)
                    # If successful then display a message to the user
                    messagebox.showinfo("Info", "Selected staff members exported to Excel successfully!")

        except sqlite3.Error as e:
            # If there is an SQL error then display a warning
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            # Close the database connection
            self.conn.close()

if __name__ == "__main__":
    # Load up the Login Window
    app = loginWindow()
    # Start the program
    app.mainloop()
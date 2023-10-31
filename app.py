import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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
        ttk.Button(self, text="Clients", command=self.WIP_window).pack(pady=5)
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

    def open_staff(self):
        staff_page(self)

    def WIP_window(self):
        pass

class appointments_page(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Appointments")
        self.geometry("500x600")

        heading = ttk.Frame(self)
        heading.pack(pady=10, padx=10, anchor='w')

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(9, 9)
        logo_label = ttk.Label(heading, image=self.logo)
        logo_label.grid(row=0, column=1, padx=10, sticky='e')

        title = ttk.Label(heading, text="Appointments")
        title.grid(row=0, column=0, padx=10, sticky='w')

        appointments_table = ttk.Treeview(self, columns=('Client Name', 'Staff Name', 'Service', 'Time & Date', 'Status'), show='headings', height=10)

        appointments_table.column('Client Name', width=100)
        appointments_table.column('Staff Name', width=100)
        appointments_table.column('Service', width=75)
        appointments_table.column('Time & Date', width=150)
        appointments_table.column('Status', width=50)

        appointments_table.heading('Client Name', text='Client Name')
        appointments_table.heading('Staff Name', text='Staff Name')
        appointments_table.heading('Service', text='Service')
        appointments_table.heading('Time & Date', text='Time & Date')
        appointments_table.heading('Status', text='Status')
        appointments_table.pack(pady=20)

        menu_frame = ttk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        view_appointment = ttk.Button(menu_frame, text="View")
        view_appointment.grid(row=0, column=0, padx=5)

        add_appointment = ttk.Button(menu_frame, text="Add")
        add_appointment.grid(row=0, column=1, padx=5)

        edit_appointment = ttk.Button(menu_frame, text="Edit")
        edit_appointment.grid(row=0, column=2, padx=5)

        delete_appointment = ttk.Button(menu_frame, text="Delete")
        delete_appointment.grid(row=0, column=3, padx=5)

        export_frame = ttk.Frame(self)
        export_frame.pack(pady=5)

        export_button = ttk.Button(export_frame, text="Export")
        export_button.grid(row=0, column=0, padx=5)

        exportall_button = ttk.Button(export_frame, text="Export All")
        exportall_button.grid(row=0, column=1, padx=5)

        services_button = ttk.Button(self, text="View and Edit services")
        services_button.pack(pady=10)

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
        self.staff_table.column('DOB', width=75)
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
        status_entry = ttk.OptionMenu(add_staff_frame, self.status_selection, status_options[0], *status_options)
        status_entry.grid(row=7, column=1)

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
                    staff_gender_entry = ttk.OptionMenu(edit_staff_frame, gender_selection, selected_gender, *gender_options)
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

                    status_label = tk.Label(edit_staff_frame, text="Status:")
                    status_label.grid(row=4, column=0)
                    status_options = ["Currently Employed", "Previously Employed", "Not Employed", "Other"]
                    status_var = tk.StringVar(value=row[8])
                    status_entry = ttk.OptionMenu(edit_staff_frame, status_var, *status_options)
                    status_entry.grid(row=7, column=1)

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

        num_selected = len(selected_items)
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {num_selected} staff member(s)?")
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
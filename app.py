import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import bcrypt


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
        self.geometry("800x600")

        self.logo = tk.PhotoImage(file='img_fit1sttherapy_logo.png').subsample(3, 3)
        tk.Label(self, image=self.logo).pack(pady=5)

        self.main_frame = tk.Frame(self)
        self.main_frame.pack(expand=True, pady=20)

        button_width = 20
        button_height = 3
        font_size = (None, 14)

        button_appointments_clients = tk.Button(self.main_frame, text="Appointments & Clients",
                                                command=self.open_appointmentsandclients_page,
                                                width=button_width,
                                                height=button_height,
                                                font= font_size)
        button_appointments_clients.grid(row=0, column=0, padx=10, pady=5, sticky='ew')

        button_staff = tk.Button(self.main_frame, text="Staff",
                                 command=self.some_function,
                                 width=button_width,
                                 height=button_height,
                                 font=font_size)
        button_staff.grid(row=0, column=1, padx=10, pady=5, sticky='ew')

        button_transactions = tk.Button(self.main_frame, text="Transactions",
                                        command=self.some_function,
                                        width=button_width,
                                        height=button_height,
                                        font=font_size)
        button_transactions.grid(row=0, column=2, padx=10, pady=5, sticky='ew')

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)

        button_logout = tk.Button(self.main_frame, text="Logout",
                                  command=self.logout,
                                  font=(None, 12))
        button_logout.grid(row=1, column=0, columnspan=3, pady=30)

    def open_appointmentsandclients_page(self):
        self.main_frame.pack_forget()
        appointmentsandclientsPage(master=self).pack(expand=True, fill='both')

    def show_main_frame(self):
        self.main_frame.pack(expand=True, pady=20)

    def some_function(self):
        pass

    def logout(self):
        current_logged_in_user = None
        self.destroy()
        app = loginWindow()
        app.mainloop()

class appointmentsandclientsPage(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master = master

        buttons_frame = tk.Frame(self)
        buttons_frame.pack(pady=30)

        button_width = 20
        button_height = 3
        font_size = (None, 14)

        button_appointments_services = tk.Button(buttons_frame, text="Appointments & Services",
                                                 width=button_width,
                                                 height=button_height,
                                                 font=font_size)
        button_appointments_services.grid(row=0, column=0, padx=10)

        button_clients = tk.Button(buttons_frame, text="Clients", 
                                   width=button_width, height=button_height, 
                                   font=font_size)
        button_clients.grid(row=0, column=1, padx=10)

        button_back = tk.Button(self, text="Back to Main Menu", command=self.back_to_main, font=(None, 12))
        button_back.pack(pady=20)

    def back_to_main(self):
        self.master.show_main_frame()
        self.destroy()


if __name__ == "__main__":
    app = loginWindow()
    app.mainloop()
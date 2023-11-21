import tkinter as tk
from tkinter import Button
from tkcalendar import DateEntry

def get_date():
    time = time_entry.get()
    date = date_entry.get()
    print(f"{time}, {date}")

root = tk.Tk()

time_label = tk.Label(root, text="[hh:mm] 24h Time:")
time_label.grid(row=0, column=0)
time_entry = tk.Entry(root, width=5)
time_entry.grid(row=0, column=1)

date_label = tk.Label(root, text="[dd-mm-yyyy] Date:")
date_label.grid(row=1, column=0)
date_entry = DateEntry(root, date_pattern="dd-mm-yyyy", width=10)
date_entry.grid(row=1, column=1)

datetime_submit = Button(root, text="Submit", command=get_date)
datetime_submit.grid(row=2, column=0, columnspan=4)

root.mainloop()

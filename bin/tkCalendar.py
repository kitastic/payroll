# Import Required Library
from tkinter import *
from tkcalendar import Calendar

# Create Object
root = Tk()
# Set geometry
root.geometry("400x800")
def start_date():
    date.config(text="Selected Date is: " + cal.get_date())

def end_date():
    date.config(text="Selected Date is: " + cal2.get_date())

# Add Calendar
cal = Calendar(root, selectmode='day', firstweekday='sunday')
cal.pack(pady=20)


# Add Button and Label
Button(root, text="Start Date",
       command=start_date).pack(pady=20)

# Add Calendar
cal2 = Calendar(root, selectmode='day', firstweekday='sunday')
cal2.pack(pady=20)

# Add Button and Label
Button(root, text="End Date",
       command=end_date).pack(pady=20)

date = Label(root, text="")
date.pack(pady=20)
# Execute Tkinter
root.mainloop()
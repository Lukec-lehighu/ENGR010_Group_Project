import tkinter as tk
import sv_ttk #dark ttk theme
from TkinterFrames import *

root = tk.Tk()
root.title('Data analysis program')
root.geometry("1020x500")

App(root).pack(side="top", fill="both", expand=True)
sv_ttk.set_theme("dark") #make the app evil (dark theme)
root.mainloop()
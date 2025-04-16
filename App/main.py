import tkinter as tk
import sv_ttk #dark ttk theme
from TkinterFrames import * #import all the custom classes

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Data analysis program')
    root.geometry("1320x600")

    App(root).pack(side="top", fill="both", expand=True) #add the main app to the root of the window
    sv_ttk.set_theme("dark") #make the app evil (dark theme)
    root.mainloop() #run that thang
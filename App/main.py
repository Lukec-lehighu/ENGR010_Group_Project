import tkinter as tk
import sv_ttk #dark ttk theme
from TkinterFrames import App #import main app

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Data analysis program')
    root.geometry("1320x600")

    App(root).pack(side="top", fill="both", expand=True) #add the main app to the root of the window
    sv_ttk.set_theme("dark") #set dark mode for more professional app appearance 
    root.mainloop() #run the app
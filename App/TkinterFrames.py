import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from ttkbootstrap.scrolled import ScrolledText

import pandas as pd
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import seaborn as sns
import numpy as np
import json
import os

#useful functions:
#chatgpt generated
def import_file(filename):
    """
    Imports a file and stores its data in a structured format.
    Supports CSV, Excel, JSON, and text files.
    Returns a Pandas DataFrame if possible; otherwise, returns raw text or structured data.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")

    file_extension = os.path.splitext(filename)[-1].lower()

    try:
        if file_extension in ['.csv']:
            return pd.read_csv(filename)
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(filename)
        elif file_extension in ['.json']:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return pd.json_normalize(data) if isinstance(data, list) else data
        elif file_extension in ['.txt']:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise RuntimeError(f"Error processing file '{filename}': {str(e)}")


#the image part
class DataVisualizer(ttk.Frame):
    def __init__(self, parent, data_class):
        super().__init__(parent)
        self.data_class = data_class
        
        self.display_panel = ttk.Label(self)
        self.display_panel.pack(fill='both', expand=True, padx=10)

    def update(self, mode='', x_vals=[], y_vals=[]):
        """
        Given a given mode, update the graph data and set the display window to reflect this change in graph
        """
        if mode == 'corr_mat':
            corr = self.data_class.loaded_data.corr()
            sns.heatmap(corr, 
                xticklabels=corr.columns.values,
                yticklabels=corr.columns.values).get_figure().savefig("temp.png")

            img = Image.open('temp.png')
            img = img.resize((500, 500), Image.LANCZOS)
            self.imgtk = ImageTk.PhotoImage(img)
            self.display_panel.config(image=self.imgtk)
        elif mode == 'scatter':
            pass
        elif mode == 'hist':
            pass
        elif mode == 'bwp':
            pass


#basic analysis and summary of imported data
class DataPreview(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.data_label = ScrolledText(self, padding=5, height=10, width=70, vbar=True)
        self.data_label.insert(tk.INSERT, "No data loaded", 'body')
        self.data_label.tag_config('body', foreground="white")
        self.data_label.pack(side='top', fill='both', expand=True, padx=10)

    def update(self, df):
        new_text = ''
        for col in df.columns:
            new_text += f'Column: {col}\n'
            if is_numeric_dtype(df[col]):
                #calculate some numeric stats
                new_text += f' - Avg: {round(df[col].mean(), 2)}\n'
                new_text += f' - Min: {df[col].min()}, Max: {df[col].max()}\n'
            else:
                new_text += f' - Number of unique items: {df[col].nunique()}\n'
                
        self.data_label.delete('1.0', tk.END)
        self.data_label.insert(tk.INSERT, new_text, 'body')


class AxisSelection(ttk.Frame):
    def __init__(self, parent, df):
        super().__init__(parent)

        options = [col for col in df.columns if is_numeric_dtype(df[col])]

        self.x_option = tk.StringVar(self)
        self.x_axis_select = ttk.OptionMenu(
            self,
            self.x_option,
            'Select X Data',
            *options,
            command=self.options_changed
        )
        self.y_option = tk.StringVar(self)
        self.y_axis_select = ttk.OptionMenu(
            self,
            self.y_option,
            'Select Y Data',
            *options,
            command=self.options_changed
        )

        self.x_option.pack(side='left', fill='both', expand=True)
        self.y_option.pack(side='right', fill='both', expand=True)

    def get_options(self):
        return

    def options_changed(self):
        pass

#all the buttons to make stuff happen
class SelectionPanel(ttk.Frame):
    def __init__(self, parent, data_visualizer):
        super().__init__(parent)
        self.data_visualizer = data_visualizer

        left_side = ttk.Frame(self)
        right_side = ttk.Frame(self)

        #left side items
        mode_options = ['Graph', 'Correlation Matrix']
        self.mode_option = tk.StringVar(self)
        self.mode_dropdown = ttk.OptionMenu(
            left_side,
            self.mode_option,
            'Select Mode',
            *mode_options,
            command=self.options_changed
        )

        graph_options = ['Scatter', 'Histogram', 'BW Plot']
        self.graph_option = tk.StringVar(self)
        self.graph_dropdown = ttk.OptionMenu(
            left_side,
            self.graph_option,
            'Select Graph',
            *graph_options,
            command=self.options_changed
        )

        anal_options = ['K-Means', 'Classification', 'Regression']
        self.anal_option = tk.StringVar(self)
        self.anal_dropdown = ttk.OptionMenu(
            left_side,
            self.anal_option,
            'Analysis Mode',
            *anal_options,
            command=self.options_changed
        )

        #right side_items
        #TODO: maybe put in a left side

        left_side.pack(side='left', fill='both', expand=True)
        right_side.pack(side='right', fill='both', expand=True)
        

    def options_changed(self, *args):
        self.update_visibility()
    
    def reset_visibility(self):
        """
        Unpacks all items from frame to reset the structure of the UI
        """
        self.mode_dropdown.pack_forget()
        self.graph_dropdown.pack_forget()
        self.anal_dropdown.pack_forget()
    
    def update_visibility(self):
        """
        Determines what items will be visible
        """
        self.reset_visibility()

        self.mode_dropdown.pack(side='top', fill='both', expand=True, pady=3)
        if self.mode_option.get() == 'Correlation Matrix':
            self.data_visualizer.update('corr_mat')
        elif self.mode_option.get() == 'Graph':
            #add the new dropdowns to the menu visible when on Graph mode
            self.graph_dropdown.pack(side='top', fill='both', expand=True, pady=3)
            self.anal_dropdown.pack(side='top', fill='both', expand=True, pady=3)
            
            self.data_visualizer.update('')


#main app structure and functions
class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        top_layer = ttk.Frame(self)
        self.import_btn = ttk.Button(top_layer, text="Import data", command=self.select_file)

        middle_layer = ttk.Frame(self)
        self.data_preview = DataPreview(middle_layer)
        self.data_visualizer = DataVisualizer(middle_layer, self)
        self.selection_panel = SelectionPanel(middle_layer, self.data_visualizer)

        bottom_layer = ttk.Frame(self)
        self.status_text = ttk.Label(bottom_layer, text="")
        
        #top layer
        self.import_btn.pack(side='left', padx=10, pady=10)
        top_layer.pack(side='top', fill='both')

        #middle layer
        self.data_preview.pack(side='left', padx=5, pady=5)
        self.selection_panel.pack(side='left', padx=5, pady=5)
        self.data_visualizer.pack(side='right', padx=5, pady=5)
        middle_layer.pack(fill='both', expand=True)

        #bottom layer
        self.status_text.pack(side='left', padx=10, pady=10)
        bottom_layer.pack(side='bottom', fill='both')

        self.loaded_data = None

    def select_file(self):
        """
        Uses tkinter to open a file exploration panel to allow the user to select a file.
        Uses the import_file function to load the file into a PD object.
        Runs some basic data cleaning on loaded data
        """
        filename = askopenfilename() # get file location using tkinter
        try:
            self.loaded_data = import_file(filename)
            self.loaded_data = self.loaded_data.fillna(0)
            self.status_text.config(text='Data loaded!', foreground='green')
            self.selection_panel.update_visibility()

            #display some basic analysis features
            self.data_preview.update(self.loaded_data)
        except Exception as e:
            print(e)
            self.status_text.config(text="Can't open file", foreground='red')
#UI imports
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from ttkbootstrap.scrolled import ScrolledText

#KNN imports
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix

#misc imports
import pandas as pd
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import seaborn as sns
import scipy
import json
import os

#useful function:
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
#chatgpt generated function above  

#The part of the UI that shows the generated graphs
class DataVisualizer(ttk.Frame):
    """
    The DataVisualizer Frame takes loaded data and renders and displays a graph to the GUI depending on a number of settings
    Settings will be selected from both the SelectionPanel and the AxisSelection Frames
    """
    def __init__(self, parent, data_class):
        super().__init__(parent)
        self.data_class = data_class
        
        self.display_panel = ttk.Label(self)
        self.info_panel = ttk.Label(self, text='')

        self.info_panel.pack(side='top', fill='both', pady=5)
        self.display_panel.pack(side='top', fill='both', expand=True, padx=10)

        self.mode = ''
        self.axis_selection = None

    def update(self, mode='', axis_selection=None):
        """
        Given a given mode, update the graph data and set the display window to reflect this change in graph
        """
        self.info_panel.config(text='')

        if mode == '':
            mode = self.mode
        elif mode!='Reset':
            if self.mode != mode:
                #change detected, reset graph
                plt.clf()
                self.mode = mode
                if mode!='corr_mat':
                    return # don't render new graph with old data (prevent potential errors)
            self.mode = mode

        #assign an internal reference to get selected data points
        if axis_selection:
            self.axis_selection = axis_selection

        show_graph = False #whether to render the temp.png to the GUI or not
        if mode == 'corr_mat':
            #use sns to generate a heatmap
            corr = self.data_class.loaded_data.corr()
            sns.heatmap(corr, 
                xticklabels=corr.columns.values,
                yticklabels=corr.columns.values).get_figure().savefig("temp.png", bbox_inches="tight") #save to temp file

            show_graph = True #set flag to render new graph
        elif mode == 'Scatter' and self.axis_selection:
            try:
                #attempt to get the selected columns from the loaded data
                choices = self.axis_selection.get_options()
                sns.scatterplot(data=self.data_class.loaded_data, x=choices[0], y=choices[1]).get_figure().savefig("temp.png", bbox_inches="tight")
                show_graph = True
            except:
                return #this is here to prevent a key error when the user only has selected one option for the data axis (choices will not be a df column)
        elif mode == 'Bar':
            try:
                choice = self.axis_selection.get_options()
                data = self.data_class.loaded_data[choice]
            except:
                return # just ignore the error it's probably fine (prevent key error as usual)
            
            sns.countplot(x=data, palette='Set2').get_figure().savefig("temp.png", bbox_inches="tight")
            show_graph = True
        elif mode == 'Histogram':
            try:
                choice = self.axis_selection.get_options()
                data = self.data_class.loaded_data[choice]
            except:
                return # once again ignoring these errors since they aren't important
            
            plt.clf()
            plt.xlabel(choice)
            plt.hist(data)
            plt.savefig('temp.png')

            show_graph = True
        elif mode == 'Reset':
            #reset the plt graph
            plt.clf()
            plt.savefig('temp.png')
            show_graph = True
        elif mode == 'KNN':
            self.knn()

        #assumes the code above actually created a temp.png when this is true
        if show_graph:
            self.show_graph()

    def show_graph(self):
        """
            Simple function to take a temporary file and render it to the display panel
        """
        #load image from temporary file and display in frame's panel
        img = Image.open('temp.png')
        img = img.resize((600, 500), Image.LANCZOS)
        self.imgtk = ImageTk.PhotoImage(img)
        self.display_panel.config(image=self.imgtk)

    def regression(self):
        """
            Uses a combination of sns regplot and scipy to graph the linear regression line given the user selected data
            and print the calculated line values in y=mx+b form
        """
        try:
            #attempt to get the selected columns from the loaded data
            choices = self.axis_selection.get_options()
            sns.regplot(data=self.data_class.loaded_data, x=choices[0], y=choices[1], scatter=False).get_figure().savefig("temp.png", bbox_inches="tight")

            #calculating the regplot information for displaying
            slope, intercept, r, _, _ = scipy.stats.linregress(x=self.data_class.loaded_data[choices[0]],
                                                                y=self.data_class.loaded_data[choices[1]])
            
            #display calculated information in the info_panel
            self.info_panel.config(text=f'y = {round(slope,2)}x + {round(intercept,2)}\nr² = {round(r**2, 2)}', foreground='#038cfc')
            self.show_graph()
        except:
            pass #no reason for this to error unless the user did something wrong, so no reason to make the whole code break

    def knn(self):
        """
            Creates a KNN model, creates test and training data, and fits the model
            The output of this function is a confidence matrix of the created model
            The matrix is then rendered to the screen using show_graph()
        """
        try: #once again putting everything in try-except blocks to prevent errors from printing when user doesn't select data axis (intentional)
            choice = self.axis_selection.get_options()

            #extract data
            y = self.data_class.loaded_data[choice]
            x = self.data_class.loaded_data.copy()

            #drop prediction column and all other non-numeric data
            x = x.drop(columns=[choice,])
            x = x.select_dtypes(['number'])

            #create train test splits
            X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.30)

            #create and fit model
            knn = KNeighborsClassifier(n_neighbors=5)
            knn.fit(X_train, y_train)

            #test model
            y_pred = knn.predict(X_test)

            #generate conf
            conf_matrix = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(conf_matrix, annot=True, cmap="Blues", fmt="d", xticklabels=y.unique(), yticklabels=y.unique())
            plt.xlabel("Predicted Label")
            plt.ylabel("True Label")
            plt.savefig('temp.png')

            self.info_panel.config(text='') #reset the info text
            self.show_graph() #update display
        except:
            pass
        


#basic analysis and summary of imported data
class DataPreview(ttk.Frame):
    """
    The DataPreview class is responsible for writing a simple overview of the statistics of the data.
    Displays stats such as mean, min, max, and number of unique items
    """
    def __init__(self, parent, data_visualizer):
        super().__init__(parent)
        self.data_visualizer = data_visualizer #to be passed to the axis selection class

        self.title = ttk.Label(self, text="Loaded Data Summary:")
        self.title.pack(side='top', fill='both', expand=True, pady=5, padx=15)

        self.data_label = ScrolledText(self, padding=5, height=10, width=70, vbar=True)
        self.data_label.insert(tk.INSERT, "No data loaded", 'body')
        self.data_label.tag_config('body', foreground="white")
        self.data_label.pack(side='top', fill='both', expand=True, padx=10)

        self.axis_selection = None
        self.df = pd.DataFrame()

    def update(self, df):
        self.df = df
        new_text = ''
        for col in df.columns:
            new_text += f'{col}:\n'
            if is_numeric_dtype(df[col]):
                #calculate some numeric stats
                new_text += f' - Avg: {round(df[col].mean(), 2)}\n'
                new_text += f' - Min: {df[col].min()}, Max: {df[col].max()}\n'
            else:
                new_text += f' - Number of unique items: {df[col].nunique()}\n'
                
        self.data_label.delete('1.0', tk.END)
        self.data_label.insert(tk.INSERT, new_text, 'body')

    #don't ask why this is here, logically it doesn't make sense, but it makes sense if you look at which UI elements are bound together
    def show_axis_selection(self, knn_mode=False):
        #delete old pack to make room for new object
        if self.axis_selection:
            self.axis_selection.pack_forget() 

        if knn_mode:
            self.axis_selection = AxisSelection(self, self.df, self.data_visualizer, categorical=True, single=True, pred_name=True)
            self.axis_selection.pack(side='bottom', fill='both', expand=True, pady=5)
        else:
            #create axis selection
            if self.data_visualizer.mode == 'Scatter':
                self.axis_selection = AxisSelection(self, self.df, self.data_visualizer, categorical=False, single=False)
                self.axis_selection.pack(side='bottom', fill='both', expand=True, pady=5)
            elif self.data_visualizer.mode == 'Bar':
                self.axis_selection = AxisSelection(self, self.df, self.data_visualizer, categorical=True, single=True)
                self.axis_selection.pack(side='bottom', fill='both', expand=True, pady=5)
            elif self.data_visualizer.mode == 'Histogram':
                self.axis_selection = AxisSelection(self, self.df, self.data_visualizer, categorical=False, single=True)
                self.axis_selection.pack(side='bottom', fill='both', expand=True, pady=5)

class AxisSelection(ttk.Frame):
    """
    The AxisSelection frame allows for the user to select from a dropdown which columns of the loaded data
    will be used to render the graphs.
    """
    def __init__(self, parent, df, data_visualizer, categorical=False, single=False, pred_name=False):
        super().__init__(parent)
        self.data_visualizer = data_visualizer
        self.categorical = categorical
        self.single = single

        options = []
        if categorical:
            options = [col for col in df.columns if not is_numeric_dtype(df[col]) and df[col].nunique()<=10] #not numeric data that has 10 or less unique categories
        else:
            options = [col for col in df.columns if is_numeric_dtype(df[col])] #numeric data only

        #determining the name of the x selection dropdown (depends on mode)
        x_selection_name = 'Select X Data' #default
        if single:
            if pred_name:
                x_selection_name = 'Select Prediction Class'
            else:
                x_selection_name = 'Select Data'

        self.x_option = tk.StringVar(self)
        self.x_axis_select = ttk.OptionMenu(
            self,
            self.x_option,
            x_selection_name,
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

        self.x_axis_select.pack(side='left', fill='both', padx=10)
        if not single:
            self.y_axis_select.pack(side='right', fill='both', padx=10)

    def get_options(self):
        if self.single:
            return self.x_option.get()

        return self.x_option.get(), self.y_option.get()

    def options_changed(self, *args):
        self.data_visualizer.update(axis_selection=self)

#all the buttons to make stuff happen
class SelectionPanel(ttk.Frame):
    """
    The SelectionPanel frame renders buttons and dropdowns that the user can use to manipulate the analysis of the data
    Keeps track of what display modes are currently selected
    """
    def __init__(self, parent, data_visualizer, data_preview):
        super().__init__(parent)
        self.data_visualizer = data_visualizer
        self.data_preview = data_preview

        left_side = ttk.Frame(self)
        right_side = ttk.Frame(self)

        #left side items
        mode_options = ['Graph', 'Correlation Matrix', 'KNN']
        self.mode_option = tk.StringVar(self)
        self.mode_dropdown = ttk.OptionMenu(
            left_side,
            self.mode_option,
            'Select Mode',
            *mode_options,
            command=self.options_changed
        )

        graph_options = ['Scatter', 'Bar', 'Histogram']
        self.graph_option = tk.StringVar(self)
        self.graph_dropdown = ttk.OptionMenu(
            left_side,
            self.graph_option,
            'Select Graph',
            *graph_options,
            command=self.options_changed
        )

        self.reset_btn = ttk.Button(left_side, text="Reset Graph", command=lambda: self.data_visualizer.update(mode='Reset'))

        #right side items
        self.regression_btn = ttk.Button(right_side, text='Regression', command=lambda: self.data_visualizer.regression())

        left_side.pack(side='left', fill='both', expand=True, padx=5)
        right_side.pack(side='right', fill='both', expand=True)
        

    def options_changed(self, *args):
        self.update_visibility()
    
    def reset_visibility(self):
        """
        Unpacks all items from frame to reset the structure of the UI
        """
        self.mode_dropdown.pack_forget()
        self.graph_dropdown.pack_forget()
        self.reset_btn.pack_forget()
        self.regression_btn.pack_forget()
    
    def update_visibility(self):
        """
        Determines what items will be visible
        Starts by hiding all objects and only shows UI elements depending on what mode is selected by the user
        """
        self.reset_visibility()

        self.mode_dropdown.pack(side='top', fill='both', expand=True, pady=3)

        if self.mode_option.get() == 'Correlation Matrix':
            self.data_visualizer.update('corr_mat')
        elif self.mode_option.get() == 'Graph':
            #add the new dropdowns to the menu visible when on Graph mode
            self.graph_dropdown.pack(side='top', fill='both', expand=True, pady=3)
            self.reset_btn.pack(side='top', fill='both', expand=True, pady=3)

            #only show the option to do linear regression if in scatterplot mode
            if self.graph_option.get() == 'Scatter':
                self.regression_btn.pack(side='top', fill='both', pady=3)

            #update the UI visualization and selection options
            self.data_visualizer.update(mode=self.graph_option.get())
            self.data_preview.show_axis_selection()
        elif self.mode_option.get() == 'KNN':
            self.data_preview.show_axis_selection(knn_mode=True)
            self.data_visualizer.mode='KNN'

#main app structure and functions
class App(ttk.Frame):
    """
    Main App rendered on the root of the tkinter window. 
    Uses the custom frames above to create the GUI
    """
    def __init__(self, parent):
        super().__init__(parent)

        top_layer = ttk.Frame(self)
        self.import_btn = ttk.Button(top_layer, text="Import data", command=self.select_file)

        middle_layer = ttk.Frame(self)
        self.data_visualizer = DataVisualizer(middle_layer, self)
        self.data_preview = DataPreview(middle_layer, self.data_visualizer)
        self.selection_panel = SelectionPanel(middle_layer, self.data_visualizer, self.data_preview)

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

        self.loaded_data = pd.DataFrame()

    def select_file(self):
        """
        Uses tkinter to open a file exploration panel to allow the user to select a file.
        Uses the import_file function to load the file into a PD object.
        Runs some basic data cleaning and prepping on loaded data
        """
        filename = askopenfilename() # get file location using tkinter
        try:
            #try prompting the user to select a file from their system
            self.loaded_data = import_file(filename)

            #prep data
            self.loaded_data = self.loaded_data.fillna(0)
            for col in self.loaded_data.columns:
                #convert boolean entries to categorical
                if self.loaded_data[col].dtypes =='bool':
                    self.loaded_data[col] = self.loaded_data[col].astype('category')

            #set status text
            self.status_text.config(text='Data loaded!', foreground='green')
            self.selection_panel.update_visibility()

            #display some basic analysis features
            self.data_preview.update(self.loaded_data)
        except Exception as e:
            print(e) # useful for debugging this nightmare of a file
            self.status_text.config(text="Can't open file", foreground='red')
import os
import tkinter as tk
from tkinter import Tk
from tkinter.filedialog import askdirectory
from tkinter import Toplevel, Checkbutton, Button, IntVar, Label, Scrollbar, Canvas

class loading:
    
    """
    The loader class establishes a path containing a study directory (sets of images pertaining to an animal or phantom) that the user wishes to process. It abstracts through the directory until it locates the paths of relevant 3D images.
    """

    def __init__(self, base_path=None):

        self.base_path = base_path if base_path else self.select_directory()
        print(f"Base path: {self.base_path}")
        
        self.CTimages = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
        self.CTimages.sort
        print(f"Time series in directory: {self.CTimages}")


        self.time_series = {}  # Dictionary of first order abstraction in Philips study folder format are multiple acquisitions of the patient/animal
        self.path_to_time_series() # Function that retrieves all time-series directories

        self.material_decomposition = {} # Dictionary of second order abstraction where integrated (conventional) or spectral sampling of the source is used 
        self.path_to_material_decomposition() # Function that retrieves both material decomposition directories

        self.dicom_files = {}  # Dictionary to store 3rd and 4th order abstraction with the 3rd order being the directory map_decomps are stored and 4th being the dicom files
        self.path_to_map_decomps() # Function that retrieves dicom file paths
        self.display_selection_gui()
    
    def select_directory(self):
        # Hide the main Tkinter window
        root = Tk()
        root.withdraw()
        
        # Open the file explorer and prompt the user to select a directory
        selected_directory = askdirectory(title="Select a Study Directory")
        
        # Return the selected directory path
        return selected_directory


    def path_to_time_series(self):
        """
        This builds the path to the directory that stores image reconstruction folders. 1st order of abstraction in the Philips SPCCT prototype folder.
        """
        for subdir in self.CTimages:
            subdir_path = os.path.join(self.base_path, subdir)
            # Initialize an empty list to store contents of the current subdirectory
            contents = []
            
            try:
                # List all items in the current subdirectory
                items = os.listdir(subdir_path)
                if items:  # Check if there are items to display
                    for item in items:
                        item_path = os.path.join(subdir_path, item)
                        if os.path.isdir(item_path):
                            if "SBI" not in item:  # Skip subdirectories named "SBI"
                                contents.append(f"  Reconstruction: {item}")
                        else:
                            contents.append(f"  File: {item}")
                else:
                    contents.append("  (Empty)")
            except Exception as e:
                contents.append(f"  Error accessing {subdir_path}: {e}")
            
            # Store the contents in the dictionary
            self.time_series[subdir] = contents
            
            #Print the contents for immediate feedback
            #print(f"Contents of time-series: '{subdir}':")
            #print("\n".join(contents))
            #print()  # Blank line for better readability

    def path_to_material_decomposition(self):
        """
        This builds upon the path set by path_to_time_series(). 2nd level of abstraction in Philips SPCCT prototype folder.
        """
        for subdir, contents in self.time_series.items():
            subdir_path = os.path.join(self.base_path, subdir)
            
            # Initialize an empty dictionary to store the contents of volume directories
            reconstruction = {}
            
            for item in contents:
                item_name = item.split(': ')[-1]
                item_path = os.path.join(subdir_path, item_name) #Add to the base path to construct the direct path to the dicom file
                
                if os.path.isdir(item_path):
                    # Initialize a list to store the contents of the volume directory
                    material_decomposition_contents = []
                    
                    try:
                        # List all items in the current volume directory
                        items = os.listdir(item_path)
                        if items:  # Check if there are items to display
                            for material_decomposition_item in items:
                                material_decomposition_path = os.path.join(item_path, material_decomposition_item)
                                if os.path.isdir(material_decomposition_path):
                                    material_decomposition_contents.append(f"    Material decomposition: {material_decomposition_item}")
                                else:
                                    material_decomposition_contents.append(f"    File: {material_decomposition_item}")
                        else:
                            material_decomposition_contents.append("    (Empty)")
                    except Exception as e:
                        material_decomposition_contents.append(f"    Error accessing {item_path}: {e}")
                    
                    # Store the contents in the dictionary
                    reconstruction[item_name] = material_decomposition_contents
            
            # Store the volume contents in the main dictionary
            self.material_decomposition[subdir] = reconstruction
            
            # Print the contents for immediate feedback
            #print(f"Time-series: '{subdir}':")
            #for material_decomposition_contents, contents in reconstruction.items():
            #    print(f"  Contents of '{material_decomposition_contents}':")
            #    print("\n".join(contents))
            #    print()  # Blank line for better readability

    def path_to_map_decomps(self):
        """
        This method completes the path to all dicom files in a directory and stores them in a dictionary. This is the final 3rd and 4th levels of abstraction in  the Philips SPCCT prototype output folder.
        """
        for subdir, map_decomps in self.material_decomposition.items():
            #print(f"Processing time-series: {subdir}")
            subdir_path = os.path.join(self.base_path, subdir)
            
            # Initialize a dictionary to store folders storing dicom files and the entire 3D stack itself.
            dicom_files_in_subdir = {}
            #print(subdir)
            #print(map_decomps)

            for dicom_stack, items in map_decomps.items():

                #print(f"  Processing material decompositions: {dicom_stack}")

                # Initialize a dictionary to store the 3D stack
                threeD_stack = {}

                # Iterate through each item in the volume (directories like 'dcm', 'b_dlbasephoto', etc.)
                for item in items:
                    # Use previous function dictionary to rebuild path
                    item_name = item.split(": ")[-1].strip()
                    item_path = os.path.join(subdir_path, dicom_stack, item_name)

                    #print(f"    Checking material decomposition: {item_name}")

                    dicom_files = []

                    if os.path.isdir(item_path):
                        # Iterate over all subfolders in the item_path
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                if file.lower().endswith('.dcm'):  # Check if the file is a DICOM file
                                    dicom_files.append(os.path.join(root, file))

                    # Store the DICOM files for this specific directory in the volume
                    threeD_stack[item_name] = dicom_files

                # Store all DICOM files for each volume (like 'Conventional' or 'Spectral') in the subdirectory
                dicom_files_in_subdir[dicom_stack] = threeD_stack

            # Store the organized DICOM files for each subdirectory
            self.dicom_files[subdir] = dicom_files_in_subdir

            # Print the DICOM files for immediate feedback
            #print(f"DICOM files in '{subdir}':")
            #for threeD_stack, contents in dicom_files_in_subdir.items():
            #    print(f"  Material decomposition: {threeD_stack}")
            #    for dir_name, files in contents.items():
            #       print(f"    3D map '{dir_name}': {len(files)} DICOM files found")
            #    print()  # Blank line for better readability



    def get_time_series(self):
        """
        Returns the stored contents of all subdirectories.
        """
        return self.time_series

    def get_material_decomposition(self):
        """
        Returns the stored contents of all volume directories.
        """
        return self.material_decomposition

    def get_dicom_files(self):
        return self.dicom_files
    
    def display_selection_gui(self):
        # Create a new Tkinter window
        root = tk.Toplevel()
        root.title("Select desired time series and material decompositions:")

        # Create a Canvas widget for scrolling
        canvas = Canvas(root)
        canvas.grid(row=0, column=0, sticky='nsew')

        # Create a Frame inside the Canvas to contain all other widgets
        scrollable_frame = tk.Frame(canvas)
        
        # Create a scrollbar and link it to the Canvas
        scrollbar = Scrollbar(root, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a window inside the Canvas to hold the scrollable Frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

        def on_frame_configure(event):
            # Update the scrollregion of the Canvas to encompass the new size of the scrollable Frame
            canvas.configure(scrollregion=canvas.bbox('all'))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # Dictionary to store checkbox states for directory names
        dir_checkbox_vars = {}

        def process_selection():
            # Create a dictionary to store selected directories
            selected_dirs = {}

            # Loop through the checkboxes and find selected directories
            for time_series, map_decomps in self.dicom_files.items():
                selected_dirs[time_series] = {}
                for reconstruction, directories in map_decomps.items():
                    selected_dirs[time_series][reconstruction] = {}
                    for map_decomp, files in directories.items():
                        if dir_checkbox_vars[map_decomp].get() == 1:
                            selected_dirs[time_series][reconstruction][map_decomp] = files
            
            # Update the dicom_files dictionary to only include selected directories
            self.dicom_files = selected_dirs

            # Close the GUI window
            root.destroy()
            print("Selection complete.")
            print(f"Selected directories: {selected_dirs}")

        # Add a label for the window
        Label(scrollable_frame, text="Select Directories:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky='w')

        row_index = 1  # Initialize row index for grid placement

        # Iterate through dicom_files to create headers and checkboxes
        for ts, map_decomps in self.dicom_files.items():
            # Add a label for the current time series (header)
            ts_label = Label(scrollable_frame, text=f"Time Series: {ts}", font=('Arial', 10, 'bold'))
            ts_label.grid(row=row_index, column=0, sticky='w', pady=(10, 0))
            row_index += 1

            for reconstruction, directories in map_decomps.items():
                for dir_name, files in directories.items():
                    # Create a checkbox for each directory
                    dir_var = IntVar()
                    dir_checkbox = Checkbutton(scrollable_frame, text=f"  Material decomposition: {dir_name}", variable=dir_var)
                    dir_checkbox.grid(row=row_index, column=0, sticky='w', padx=20)
                    dir_checkbox_vars[dir_name] = dir_var
                    row_index += 1  # Increment row index for the next checkbox

        # Confirm button
        confirm_button = Button(scrollable_frame, text="Confirm Selection", command=process_selection)
        confirm_button.grid(row=row_index, column=0, columnspan=2, pady=(10, 0))

        # Adjust column and row weights to make sure the Canvas expands with window size
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        root.mainloop()
        print("outside loop")
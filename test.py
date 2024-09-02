import tkinter as tk
from tkinter import Canvas, Scrollbar, Label, Checkbutton, Button, IntVar

class GUIExample:
    def __init__(self):
        self.dicom_files = {
            'TimeSeries1': {
                'Volume1': {'Dir1': [], 'Dir2': []},
                'Volume2': {'Dir3': [], 'Dir4': []}
            },
            'TimeSeries2': {
                'Volume1': {'Dir5': [], 'Dir6': []},
                'Volume2': {'Dir7': [], 'Dir8': []}
            }
        }
        self.display_selection_gui()

    def display_selection_gui(self):
        # Create a new Tkinter window
        root = tk.Toplevel()
        root.title("Select Directories Containing DICOM Files:")

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
            for ts, map_decomps in self.dicom_files.items():
                selected_dirs[ts] = {}
                for reconstruction, directories in map_decomps.items():
                    selected_dirs[ts][reconstruction] = {}
                    for dir_name, files in directories.items():
                        if dir_checkbox_vars[dir_name].get() == 1:
                            selected_dirs[ts][reconstruction][dir_name] = files
            
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
                    dir_checkbox = Checkbutton(scrollable_frame, text=f"  Directory: {dir_name}", variable=dir_var)
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

# Create an instance of the GUIExample class
GUIExample()

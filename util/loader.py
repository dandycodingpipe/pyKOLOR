import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

class Loader:
    
    """
    The loader class establishes a path containing a study directory (sets of images pertaining to an animal or phantom) that the user wishes to process. It abstracts through the directory until it locates the paths of relevant 3D images.
    """

    def __init__(self, base_path=None):

        self.base_path = base_path if base_path else self.select_directory()
        print(f"Base path: {self.base_path}")
        
        self.directories = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
        self.directories.sort
        print(f"Time series in directory: {self.directories}")


        self.subdirectory_contents = {}  # Dictionary to store contents of each subdirectory
        self.image_class_subdirectories()

        self.volumedirectory_contents = {} # Dictionary to store contents of volume directories
        self.volume_directories()

        self.dicom_files = {}  # Dictionary to store DICOM files for each volume
        self.volume_maps()
    
    def select_directory(self):
        # Hide the main Tkinter window
        root = Tk()
        root.withdraw()
        
        # Open the file explorer and prompt the user to select a directory
        selected_directory = askdirectory(title="Select a Study Directory")
        
        # Return the selected directory path
        return selected_directory


    def image_class_subdirectories(self):
        """
        In each study directory there are image class subdirectories: conventional, spectral, and SBI. 
        These subdirectories contain 3D map files. SBI files are discarded in this step.
        """
        for subdir in self.directories:
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
                                contents.append(f"  Directory: {item}")
                        else:
                            contents.append(f"  File: {item}")
                else:
                    contents.append("  (Empty)")
            except Exception as e:
                contents.append(f"  Error accessing {subdir_path}: {e}")
            
            # Store the contents in the dictionary
            self.subdirectory_contents[subdir] = contents
            
            # Print the contents for immediate feedback
            #print(f"Contents of '{subdir}':")
            #print("\n".join(contents))
            #print()  # Blank line for better readability

    def volume_directories(self):
        """
        For each image class directory, list the contents of the volume subdirectories.
        """
        for subdir, contents in self.subdirectory_contents.items():
            subdir_path = os.path.join(self.base_path, subdir)
            
            # Initialize an empty dictionary to store the contents of volume directories
            volume_contents = {}
            
            for item in contents:
                item_name = item.split(': ')[-1]
                item_path = os.path.join(subdir_path, item_name)
                
                if os.path.isdir(item_path):
                    # Initialize a list to store the contents of the volume directory
                    volume_dir_contents = []
                    
                    try:
                        # List all items in the current volume directory
                        volume_items = os.listdir(item_path)
                        if volume_items:  # Check if there are items to display
                            for volume_item in volume_items:
                                volume_item_path = os.path.join(item_path, volume_item)
                                if os.path.isdir(volume_item_path):
                                    volume_dir_contents.append(f"    Directory: {volume_item}")
                                else:
                                    volume_dir_contents.append(f"    File: {volume_item}")
                        else:
                            volume_dir_contents.append("    (Empty)")
                    except Exception as e:
                        volume_dir_contents.append(f"    Error accessing {item_path}: {e}")
                    
                    # Store the contents in the dictionary
                    volume_contents[item_name] = volume_dir_contents
            
            # Store the volume contents in the main dictionary
            self.volumedirectory_contents[subdir] = volume_contents
            
            # Print the contents for immediate feedback
            #print(f"Volume directories in '{subdir}':")
            #for volume_dir, contents in volume_contents.items():
            #    print(f"  Contents of '{volume_dir}':")
            #    print("\n".join(contents))
            #    print()  # Blank line for better readability

    def volume_maps(self):
        """
        This method identifies the DICOM files present in every folder of each volume directory in the study.
        It organizes them into a nested dictionary structure.
        """
        for subdir, volumes in self.volumedirectory_contents.items():
            print(f"Processing subdir: {subdir}")
            subdir_path = os.path.join(self.base_path, subdir)
            
            # Initialize a dictionary to store DICOM files categorized by their volume names
            dicom_files_in_subdir = {}

            for volume_name, volume_items in volumes.items():
                print(f"  Processing volume: {volume_name}")

                # Initialize a dictionary to store DICOM files for each directory under the current volume
                dicom_files_in_volume = {}

                # Iterate through each item in the volume (directories like 'dcm', 'b_dlbasephoto', etc.)
                for item in volume_items:
                    # Extract the directory name from the item string
                    item_name = item.split(": ")[-1].strip()
                    item_path = os.path.join(subdir_path, volume_name, item_name)

                    print(f"    Checking directory: {item_name}")

                    dicom_files = []

                    if os.path.isdir(item_path):
                        # Iterate over all subfolders in the item_path
                        for root, dirs, files in os.walk(item_path):
                            for file in files:
                                if file.lower().endswith('.dcm'):  # Check if the file is a DICOM file
                                    dicom_files.append(os.path.join(root, file))

                    # Store the DICOM files for this specific directory in the volume
                    dicom_files_in_volume[item_name] = dicom_files

                # Store all DICOM files for each volume (like 'Conventional' or 'Spectral') in the subdirectory
                dicom_files_in_subdir[volume_name] = dicom_files_in_volume

            # Store the organized DICOM files for each subdirectory
            self.dicom_files[subdir] = dicom_files_in_subdir

            # Print the DICOM files for immediate feedback
            print(f"DICOM files in '{subdir}':")
            for volume_dir, volume_contents in dicom_files_in_subdir.items():
                print(f"  Volume: {volume_dir}")
                for dir_name, files in volume_contents.items():
                    print(f"    Directory '{dir_name}': {len(files)} DICOM files found")
                print()  # Blank line for better readability




    def get_subdirectory_contents(self):
        """
        Returns the stored contents of all subdirectories.
        """
        return self.subdirectory_contents

    def get_volumedirectory_contents(self):
        """
        Returns the stored contents of all volume directories.
        """
        return self.volumedirectory_contents

    def get_dicom_files(self):
        return self.dicom_files
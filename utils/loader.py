# Class for loading images from a directory

import os
import re
import pydicom
import numpy as np

class Loader:
    
    def __init__(self):
        self.base_path = None
        self.directories = [d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))]
                
    def extract_number(self, filename):
        """
        Extracts the first sequence of digits from a given filename.
        """
        match = re.search(r"\d+", filename)
        return int(match.group()) if match else 0
    
    def redefine_window(image):
        """
        Although not currently amazingly useful, I find it visually helpful to remove negative concentrations from my K-edges and have a framework for altering the intensity window
        of the conventional CT images.
        """
        window_center = image.mean()

        # K-edge specific windowing
        img_min = 0
        img_max = window_center + (200 // 2)
    
        window_image = image
        window_image[window_image < img_min] = img_min
        window_image[window_image > img_max] = img_max
    
        return window_image
    
    def fetch_data(self, study_path, sample_idx):
        """
        This function is the bread and butter of the sample class. It pulls your data according to the desired study and the desired sample.
        """
        base_path = study_path + sample_idx
        # ex. D:\copyRaw\Rabbit_AGuIX or D:\copyRaw\Phantom_XeGd
        directories = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        #directories.sort()
        directories.sort(key=self.extract_number)

        print(f"Available directories:")
        for i, directory in enumerate(directories):
            print(f"{i}: {directory}")

        #create a timepoint for each unique study in the base path
        for t, timepoint  in enumerate(directories):
            self.add_timepoint(base_path, directories, t)

        def add_timepoint(self, base_path, directories, t):
            """
            Take all the timepoints that fetch_data() identifies in order to create
            and append acquisitions to the acquisition array attribute
            """
        conventional = None
        kedge = None
        # move outside 
        
        suffixes = ["Conventional", r"Spectral/k_gadolinium"]
        time = t

        for suffix in suffixes:
            specific_path = os.path.join(base_path, directories[t], suffix)

            # Initialize the list to collect DICOM file paths
            DCMFiles = []
            for dirName, _, fileList in os.walk(specific_path):
                for filename in fileList:
                    if filename.lower().endswith('.dcm'):
                        DCMFiles.append(os.path.join(dirName, filename))

            # Check if no DICOM files were found after attempting to collect them
            if not DCMFiles:
                print(f"No DICOM files found in {specific_path}.")
                continue  # Skip the rest of this iteration and proceed with the next suffix

            print(f"{suffix} file {t+1} total DICOM files found: {len(DCMFiles)}")

            images = [pydicom.dcmread(f) for f in DCMFiles]
            images.sort(key=lambda x: float(x.ImagePositionPatient[2]))

            ConstPixelDims = (int(images[0].Rows), int(images[0].Columns), len(images))
            ArrayDicom = np.zeros(ConstPixelDims, dtype=np.float64)
    

            for dim2, img in enumerate(images):

                ArrayDicom[:, :, dim2] = rescale_image(images[1], img.pixel_array)
    
            if(suffix == "Conventional"):
                conventional = ArrayDicom
            elif(suffix == "Spectral/k_gadolinium"):
             kedge = redefine_window(ArrayDicom)
             
        #Instantiate a timepoint class object and append it to the acquisition array
        self.acquisition.append(Timepoint(t, conventional, kedge))
    #def import masks from 3d slicer


    def rescale_image(medical_image, image):
        """
        The raw intensity values of DICOM images don't correspond to either HU or mg/ml scale so we must convert them with this simple linear transformation
        """
        intercept = medical_image.RescaleIntercept
        slope = medical_image.RescaleSlope
        rescaled_image = image*slope + intercept

        return rescaled_image



    class Timepoint:
    #
        def __init__(self, time, conventional, kedge):
            self.time = time #identifier
            self.conventional = conventional # 3D array of conventional images
            self.kedge = kedge # 3D array of kedge images